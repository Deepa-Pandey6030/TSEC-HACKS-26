import os
import json
from dotenv import load_dotenv
from groq import Groq

# Load environment variables FIRST
load_dotenv()

# Now create the client with the loaded environment variable
client = Groq(
    api_key=os.getenv("XAI_API_KEY") or os.getenv("GROQ_API_KEY")
)

# --- FUNCTION 1: DYNAMIC EXTRACTION (NEW) ---
def extract_entities(text):
    """
    Reads the text and finds who is PHYSICALLY PRESENT.
    Returns: [{"name": "Alice", "status": "alive"}]
    """
    prompt = f"""
    Analyze the scene text. Extract PROPER NAMES of characters and determine their status.

    --- TEXT ---
    "{text[:1500]}"

    --- EXTRACTION RULES ---
    1. EXTRACT ONLY PROPER NAMES (e.g., "John", "Alice", "The King").
    2. DO NOT extract pronouns (he, she, him, her, they, it).
    3. DO NOT extract generic terms (the man, the woman, the doctor) unless capitalized as a proper title.
    4. IF NO NAMES ARE PRESENT, return an empty list.

    --- STATUS RULES ---
    1. "alive": The character is PHYSICALLY HERE and performing actions.
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
        # Handle potential key variations
        if "characters" in data: return data["characters"]
        if isinstance(data, list): return data
        return [] 
    except:
        return []
# --- FUNCTION 2: THE JUDGE (EXISTING) ---
def evaluate_violation(violation_type, violation_msg, scene_text, db_context):
    prompt = f"""
    You are a Strict Continuity Logic Engine. A conflict has been detected:
    
    --- CONFLICT ---
    {violation_msg} (Context: {db_context})

    --- SCENE TEXT ---
    "{scene_text[:1500]}"

    --- RULES ---
    1. Analyze if the text contains NARRATIVE DEVICES that explain this conflict.
    2. LOOK FOR:
       - Explicit phrases ("He remembered", "It was a dream").
       - TEMPORAL MARKERS (e.g., "It was 1990", "Ten years ago", "Back in the war").
       - Reality breaks ("The hologram flickered", "He looked like a ghost").
    3. If a temporal marker places the scene in the past, the verdict is INTENTIONAL.
    4. If no such cues exist, it is a CRITICAL ERROR.

    --- OUTPUT JSON ---
    {{
        "verdict": "ERROR" or "INTENTIONAL",
        "confidence": 0.0 to 1.0,
        "detailed_analysis": "Explanation referencing specific words...",
        "fix_suggestion": "Actionable advice..."
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
        return json.dumps({"verdict": "ERROR", "detailed_analysis": str(e), "fix_suggestion": "Check AI."})