import os
import json
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from neo4j import GraphDatabase
from llm_judge import evaluate_violation, extract_entities

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
AUTH = (os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "password123"))

class ChapterInput(BaseModel):
    chapter_id: int
    text_snippet: str 

class ValidationEngine:
    def __init__(self):
        self.driver = GraphDatabase.driver(URI, auth=AUTH)

    def close(self):
        self.driver.close()

    def validate_chapter(self, data: ChapterInput):
        alerts = []
        
        print(f"\n--- NEW ANALYSIS FOR CHAPTER {data.chapter_id} ---")
        extracted_chars = extract_entities(data.text_snippet)
        print(f"📝 Extracted: {extracted_chars}")

        with self.driver.session() as session:
            for char in extracted_chars:
                name = char.get("name")
                status_in_text = char.get("status")

                if status_in_text == "alive":
                    # QUERY: Look for the character (Dead OR Alive)
                    result = session.run("""
                        MATCH (c:Character) 
                        WHERE toLower(c.name) = toLower($name) 
                        RETURN c.name, c.status
                        """, name=name).single()
                    
                    # CASE 1: CHARACTER DOES NOT EXIST (The fix you asked for)
                    if not result:
                        print(f"⚠️ Unknown Character: {name}")
                        alerts.append({
                            "type": "Unknown Character",
                            "message": f"'{name}' appears in the text but is not in the database.",
                            "suggestion": f"Is this a new character? If so, please add them. If it's a typo of an existing character, please fix it.",
                            "ai_confidence": 1.0
                        })
                    
                    # CASE 2: CHARACTER EXISTS BUT IS DEAD
                    elif result['c.status'] == 'dead':
                        print(f"🚨 RESURRECTION DETECTED: {result['c.name']}")
                        
                        # Consult AI Judge
                        llm_response = evaluate_violation(
                            violation_type="Resurrection Error",
                            violation_msg=f"Database says {result['c.name']} is dead.",
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
                                "message": f"{name} is dead in DB.", 
                                "ai_confidence": 1.0
                            })
                    
                    # CASE 3: CHARACTER EXISTS AND IS ALIVE (Valid)
                    else:
                        print(f"✅ Verified: {result['c.name']} is known and alive.")

        return alerts

engine = ValidationEngine()

@app.post("/validate")
async def validate_chapter(chapter: ChapterInput):
    try:
        alerts = engine.validate_chapter(chapter)
        status = "violation" if alerts else "valid"
        return {"status": status, "alerts": alerts}
    except Exception as e:
        print(f"❌ Fatal Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))