# backend/core/orchestrator.py
import os
from groq import Groq
from core.retriever import StoryRetriever

class CriticOrchestrator:
    def __init__(self, conn):
        self.conn = conn
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.retriever = StoryRetriever(conn)

    def generate_literary_critique(self):
        # 1. GATHER EVIDENCE
        story_text = self.retriever.get_full_story_log()
        conflicts = self.retriever.get_logic_conflicts()
        
        conflict_text = "None detected."
        if conflicts:
            conflict_text = "\n".join([f"- CRITICAL: {c['name']} died at Time {c['death_time']} but acted at Time {c['action_time']}." for c in conflicts])

        # 2. THE PROMPT (The Award-Winning Author Persona)
        prompt = f"""
        SYSTEM IDENTITY:
        You are a celebrated literary critic and novelist with 30 years of experience. You have won the Booker Prize.
        Your tone is sophisticated, honest, deeply insightful, but polite. You view the user as a peer who needs the hard truth to improve.

        INSTRUCTIONS:
        Read the provided STORY LOG below. Analyze it deeply.
        Write a structured critique. Do not use generic fluff. Quote specific events from the log.

        --- DATA VAULT ---
        STORY LOG (The actual draft events):
        {story_text}

        LOGIC AUDIT (Database Consistency Check):
        {conflict_text}
        
        --- OUTPUT FORMAT ---
        Write a 'Literary Review' with these sections:
        1. **The Narrative Arc**: A high-level assessment of the story's ambition. Quote a specific event that stood out.
        2. **Structural Integrity**: Address the flow. If there are items in the 'LOGIC AUDIT', sternly but politely warn the writer that these break the fictional dream.
        3. **Character Depth**: Analyze if the characters feel consistent based on their actions in the log.
        4. **The Verdict**: A final summary of advice.

        Start your response now.
        """

        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                temperature=0.6
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Critique generation failed: {str(e)}"