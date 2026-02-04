"""
FastAPI main application entry point for NOLAN Backend.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
import json
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List, Optional
from neo4j import GraphDatabase

# Import your custom logic
from app.config import settings
from llm_judge import evaluate_violation, extract_entities 

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
PASSWORD = os.getenv("NEO4J_PASSWORD", "password123")
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

    def validate_chapter(self, data: ChapterInput):
        if not self.driver:
            raise Exception("Database not connected")

        alerts = []
        logger.info(f"--- Continuity Analysis Started for Chapter {data.chapter_id} ---")
        
        # 1. Dynamic Extraction
        extracted_chars = extract_entities(data.text_snippet)
        logger.info(f"📝 Extracted Entities: {extracted_chars}")

        with self.driver.session() as session:
            for char in extracted_chars:
                name = char.get("name")
                status_in_text = char.get("status")

                if status_in_text == "alive":
                    # 2. Strict DB Lookup
                    result = session.run("""
                        MATCH (c:Character) 
                        WHERE toLower(c.name) = toLower($name) 
                        RETURN c.name, c.status
                        """, name=name).single()
                    
                    # CASE A: Unknown Character
                    if not result:
                        logger.warning(f"⚠️ Unknown Character detected: {name}")
                        alerts.append({
                            "type": "Unknown Character",
                            "message": f"'{name}' appears in the text but is not in the database.",
                            "suggestion": f"Is this a new character? If so, please add them. If it's a typo, please fix it.",
                            "ai_confidence": 1.0
                        })
                    
                    # CASE B: Conflict (Dead but appearing Alive)
                    elif result['c.status'] == 'dead':
                        logger.warning(f"🚨 RESURRECTION DETECTED: {result['c.name']}")
                        
                        # 3. AI Judge (Uses the "Editor" Persona)
                        llm_response = evaluate_violation(
                            violation_type="Resurrection Error",
                            violation_msg=f"The database confirms {result['c.name']} is dead.",
                            scene_text=data.text_snippet,
                            db_context=f"{result['c.name']} died previously."
                        )
                        
                        try:
                            verdict = json.loads(llm_response)
                            verdict_text = verdict.get("verdict", "").upper()
                            is_intentional = verdict_text == "INTENTIONAL"
                            alert_type = "Narrative Device" if is_intentional else "Critical Error"
                            
                            alerts.append({
                                "type": alert_type,
                                "message": verdict.get("detailed_analysis"),
                                "suggestion": verdict.get("fix_suggestion"),
                                "ai_confidence": verdict.get("confidence", 0)
                            })
                        except:
                            alerts.append({
                                "type": "Critical Error", 
                                "message": f"{name} is established as dead in the story context.", 
                                "ai_confidence": 1.0
                            })
                    
                    # CASE C: Valid
                    else:
                        logger.info(f"✅ Verified: {result['c.name']} is alive.")

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

# Include any other routers you have
from app.api import creative_assistant_router
app.include_router(creative_assistant_router)

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