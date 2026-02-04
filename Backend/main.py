"""
FastAPI main application entry point for NOLAN Backend.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
import json
import difflib  # ADDED: For smart typo detection
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List, Optional
from neo4j import GraphDatabase

# Import your custom logic
from app.config import settings
# CHANGED: Imported the new Deep Logic function
from llm_judge import evaluate_logic_deeply, extract_entities 

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format=settings.log_format
)

logger = logging.getLogger(__name__)


# --- CONTINUITY VALIDATOR LOGIC ---

# 1. LOAD SECRETS FROM .ENV
URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER = os.getenv("NEO4J_USER", "neo4j")
# Preserving your specific password fallback
PASSWORD = os.getenv("NEO4J_PASSWORD", "Av7hepdWh4oJSMotGfn0saITFaas5jbjHBo5Fy3AC5E")
AUTH = (USER, PASSWORD)

class ChapterInput(BaseModel):
    chapter_id: int
    text_snippet: str 

class ContinuityValidator:
    def __init__(self):
        try:
            # AuraDB requires the driver to handle encrypted connections (neo4j+s) automatically based on URI scheme
            self.driver = GraphDatabase.driver(URI, auth=AUTH)
            self.driver.verify_connectivity()
            logger.info(f"✅ Connected to Neo4j Cloud: {URI}")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Neo4j Cloud: {e}")
            self.driver = None

    def close(self):
        if self.driver:
            self.driver.close()

    # --- ADDED: ANALYTICS ENGINE ---
    def get_analytics(self):
        """
        Fetches World Stats and the Dormancy Risk List.
        """
        if not self.driver:
            raise Exception("Database not connected")
            
        stats = {
            "total_characters": 0,
            "active_count": 0,
            "inactive_count": 0,
            "dormant_characters": []
        }

        with self.driver.session() as session:
            # 1. GENERAL CENSUS
            census_query = """
            MATCH (c:Character)
            RETURN 
                count(c) as total,
                sum(case when c.status = 'dead' OR c.status = 'inactive' then 1 else 0 end) as inactive
            """
            result = session.run(census_query).single()
            if result:
                stats["total_characters"] = result["total"]
                stats["inactive_count"] = result["inactive"]
                stats["active_count"] = result["total"] - result["inactive"]

            # 2. DORMANCY RADAR (Gap Analysis)
            # Finds characters who are ALIVE but haven't been seen in > 3 chapters
            radar_query = """
            MATCH (c:Character)
            WITH max(c.last_seen_chapter) as current_max_chapter
            MATCH (c:Character)
            WHERE c.status = 'alive' 
              AND (current_max_chapter - coalesce(c.last_seen_chapter, 0)) >= 3
            RETURN 
                c.name as name, 
                coalesce(c.last_seen_chapter, 0) as last_seen,
                (current_max_chapter - coalesce(c.last_seen_chapter, 0)) as gap
            ORDER BY gap DESC
            LIMIT 5
            """
            radar_results = session.run(radar_query)
            for record in radar_results:
                stats["dormant_characters"].append({
                    "name": record["name"],
                    "last_seen": record["last_seen"],
                    "gap": record["gap"]
                })
                
        return stats

    # --- UPDATED: VALIDATION LOGIC (Deep Context Check) ---
    def validate_chapter(self, data: ChapterInput):
        if not self.driver:
            raise Exception("Database not connected")

        alerts = []
        logger.info(f"--- Deep Logic Analysis Started for Chapter {data.chapter_id} ---")
        
        # 1. Dynamic Extraction
        extracted_chars = extract_entities(data.text_snippet)
        logger.info(f"📝 Extracted Entities: {extracted_chars}")

        # Fetch ALL character names from DB once for fuzzy matching (Optimization)
        with self.driver.session() as session:
            all_db_chars = session.run("MATCH (c:Character) RETURN c.name as name").value()

            for name in extracted_chars:
                # 2. Fetch Full Character Profile (Check EVERYONE, not just Alive)
                db_char = session.run("""
                    MATCH (c:Character) 
                    WHERE toLower(c.name) = toLower($name) 
                    RETURN c.name as name, c.status as status, c.last_seen_chapter as last_seen
                    """, name=name).single()
                
                # CASE A: Unknown Character (With Smart Typo Detection)
                if not db_char:
                    matches = difflib.get_close_matches(name, all_db_chars, n=1, cutoff=0.8)
                    if matches:
                        logger.warning(f"⚠️ Potential Typo: {name} -> {matches[0]}")
                        alerts.append({
                            "type": "Potential Typo",
                            "message": f"'{name}' is unknown, but looks similar to '{matches[0]}'.",
                            "suggestion": f"Did you mean '{matches[0]}'? If so, please correct the spelling.",
                            "ai_confidence": 0.9
                        })
                    continue

                # CASE B: DEEP LOGIC CHECK
                profile = {
                    "name": db_char["name"],
                    "status": db_char["status"],
                    "last_seen": db_char["last_seen"]
                }

                logger.info(f"🤖 Judging Logic for: {profile['name']} ({profile['status']})")

                # Send to LLM Judge
                llm_response = evaluate_logic_deeply(data.text_snippet, profile)
                
                verdict = llm_response.get("verdict", "Error")
                
                if verdict == "Critical Error":
                    alerts.append({
                        "type": "Critical Error",
                        "message": llm_response.get("analysis"),
                        "suggestion": llm_response.get("suggestion"),
                        "ai_confidence": 1.0
                    })
                elif verdict == "Intentional Device":
                    logger.info(f"ℹ️ Intentional Device detected for {name}: {llm_response.get('analysis')}")
                elif verdict == "Aligned":
                    logger.info(f"✅ {name} Aligned.")

        return alerts


# --- FASTAPI APP SETUP ---

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    
    # Initialize Validator
    try:
        app.state.validator = ContinuityValidator()
        logger.info("✅ Continuity Validator Engine Initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Continuity Validator: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down application")
    if hasattr(app.state, "validator"):
        app.state.validator.close()
        logger.info("🔒 Neo4j Connection Closed")


@app.get("/")
async def root():
    return {"status": "running", "mode": "cloud"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# --- ROUTERS (Preserved from your code) ---
from app.api import creative_assistant_router, grammar_router, autocomplete_router, nlp_router, graph_router

app.include_router(creative_assistant_router)
app.include_router(grammar_router)
app.include_router(autocomplete_router)
app.include_router(nlp_router)
app.include_router(graph_router)

# --- ADDED: ANALYTICS ENDPOINT ---
@app.get("/analytics")
async def get_analytics():
    """Returns world stats and dormancy data."""
    if not hasattr(app.state, "validator"):
         raise HTTPException(status_code=503, detail="Service unavailable")
    try:
        return app.state.validator.get_analytics()
    except Exception as e:
        logger.error(f"Analytics Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/validate")
async def validate_chapter(chapter: ChapterInput):
    """
    Endpoint to trigger the ContinuityValidator logic.
    """
    if not hasattr(app.state, "validator") or not app.state.validator.driver:
         raise HTTPException(status_code=503, detail="Cloud Database not connected")
    
    try:
        alerts = app.state.validator.validate_chapter(chapter)
        status = "violation" if alerts else "valid"
        return {"status": status, "alerts": alerts}
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- INCLUDE AUTH ROUTES ---
from app.api.auth import router as auth_router
app.include_router(auth_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )