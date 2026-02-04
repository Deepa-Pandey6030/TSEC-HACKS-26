import os
import json
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Groq Client
# Ensure GROQ_API_KEY is set in your .env file
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def extract_entities(text):
    """
    Reads the text and finds who is PHYSICALLY PRESENT.
    Ignores pronouns (he/she) and "mentions" (thoughts/memories).
    """
    prompt = f"""
    Analyze the scene text. Extract PROPER NAMES of characters and determine their status.

    --- TEXT ---
    "{text[:1500]}"

    --- EXTRACTION RULES ---
    1. EXTRACT ONLY PROPER NAMES (e.g., "John", "Alice").
    2. DO NOT extract pronouns (he, she, him, her, they, it).
    3. DO NOT extract generic terms (the man, the doctor) unless capitalized as a title.
    4. IF NO NAMES ARE PRESENT, return an empty list.

    --- STATUS RULES ---
    1. "alive": The character is PHYSICALLY HERE and performing actions (walking, talking).
    2. "dead": The text explicitly describes their dead body is present.
    3. "mentioned": The character is NOT in the room (only thought about, discussed, or seen in a photo).

    --- OUTPUT FORMAT (JSON LIST) ---
    [
        {{"name": "Character Name", "status": "alive/dead/mentioned"}}
    ]
    """
    try:
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            temperature=0
        )
        data = json.loads(completion.choices[0].message.content)
        
        # Robust handling for different JSON structures the LLM might return
        if "characters" in data: 
            return data["characters"]
        if isinstance(data, list): 
            return data
        
        return [] 
    except Exception as e:
        print(f"Extraction Error: {e}")
        return []

def evaluate_violation(violation_type, violation_msg, scene_text, db_context):
    """
    The "Judge" that decides if a conflict is an Error or a Creative Choice.
    Refined to sound like a Story Editor, not a Database Admin.
    """
    prompt = f"""
    You are an expert Story Continuity Editor. A logical contradiction has been detected in the narrative.
    
    --- CONTRADICTION ---
    {violation_msg} (Context: {db_context})

    --- SCENE TEXT ---
    "{scene_text[:1500]}"

    --- TASK ---
    Analyze the text for "Narrative Devices" that might explain this contradiction (e.g., Flashbacks, Dreams, Hallucinations).

    --- TONE RULES (CRITICAL) ---
    1. NEVER use technical terms like "database", "record", "system", or "row".
    2. ALWAYS use terms like "established story context", "narrative continuity", "canon", or "timeline".
    3. Be helpful and constructive, like a senior editor giving notes to a writer.

    --- JUDGMENT RULES ---
    1. If the text contains a TEMPORAL MARKER (e.g., "1990", "Years ago") that places it in the past -> Verdict: INTENTIONAL.
    2. If the text clearly frames the event as a dream, hallucination, or simulation -> Verdict: INTENTIONAL.
    3. If the character appears alive in the present tense with no explanation -> Verdict: ERROR.

    --- OUTPUT JSON ---
    {{
        "verdict": "ERROR" or "INTENTIONAL",
        "confidence": 0.0 to 1.0,
        "detailed_analysis": "A clear, natural explanation of the issue. Example: 'The scene depicts John acting in the present day, which contradicts the established event of his death.'",
        "fix_suggestion": "A specific creative writing suggestion. Example: 'Consider framing this as a memory by adding a phrase like \"She remembered how...\"'"
    }}
    """
    try:
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile", 
            response_format={"type": "json_object"}, 
            temperature=0.1
        )
        return completion.choices[0].message.content
    except Exception as e:
        # Fallback JSON if the LLM fails completely
        return json.dumps({
            "verdict": "ERROR", 
            "detailed_analysis": "An internal processing error occurred while analyzing the narrative.", 
            "fix_suggestion": "Please check the backend logs."
        })