import os
import json
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Groq Client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def extract_entities(text):
    """
    Step 1: Simple Extraction.
    We just want to know WHO is mentioned so we can look up their profile.
    The 'Deep Logic' function will decide if they are actually 'present'.
    """
    prompt = f"""
    Analyze the scene below and list EVERY proper name mentioned.
    
    SCENE: "{text[:4000]}"
    
    OUTPUT JSON:
    {{
        "characters": ["Name1", "Name2"]
    }}
    """
    try:
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            temperature=0
        )
        return json.loads(completion.choices[0].message.content).get("characters", [])
    except:
        return []

def evaluate_logic_deeply(scene_text, char_profile):
    """
    Step 2: The Deep Logic Analysis.
    This replaces the old 'evaluate_violation' function.
    It does not just check 'Alive/Dead'. It checks Context, Intent, and Narrative Flow.
    """
    prompt = f"""
    You are a Narrative Logic Engine. Your job is to analyze CONTEXT and INTENT, not just keywords.

    --- 1. DATABASE CONTEXT (The Truth) ---
    Name: {char_profile['name']}
    Status: {char_profile['status']} (This is the established reality)
    Last Seen: {char_profile.get('last_seen', 'Unknown')}

    --- 2. SCENE TEXT (The User's Input) ---
    "{scene_text[:2500]}"

    --- 3. YOUR TASK ---
    Analyze the character's presence in the scene against the Database Context.

    STEP A: Understand the Scene Context.
    - Is the character physically present and acting?
    - Or is this a memory, a mention, a metaphor, a dream, or a hallucination?
    - Interpret phrases like "The ghost of..." or "He felt..." literarily.

    STEP B: Compare with Database.
    - If DB says DEAD and Scene implies PHYSICAL PRESENCE -> Contradiction (Critical Error).
    - If DB says ALIVE and Scene implies PHYSICAL PRESENCE -> Aligned.
    - If DB says DEAD and Scene implies MEMORY -> Aligned (Intentional Device).

    STEP C: Determine Verdict.
    - "Aligned": The scene fits perfectly with the DB facts.
    - "Intentional Device": There is a contradiction in status, but the context (dream/flashback) explains it validly.
    - "Critical Error": There is a contradiction with NO narrative explanation (e.g., A dead man walking in the present tense).

    --- OUTPUT JSON FORMAT ---
    {{
        "verdict": "Aligned" | "Intentional Device" | "Critical Error",
        "analysis": "Explain WHY and HOW it fits or fails. Be specific about the context.",
        "suggestion": "If Critical, suggest a fix. If Aligned, leave empty."
    }}
    """
    try:
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile", 
            response_format={"type": "json_object"}, 
            temperature=0
        )
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        return {
            "verdict": "Critical Error", 
            "analysis": "AI Engine failed to parse logic.", 
            "suggestion": "Check logs."
        }