# backend/core/retriever.py
from database import Neo4jConnection

class StoryRetriever:
    def __init__(self, conn: Neo4jConnection):
        self.conn = conn

    def get_full_story_log(self):
        """Fetches the chronological story events to give the AI context."""
        query = """
        MATCH (e:Event)
        OPTIONAL MATCH (i:Identity)-[:PARTICIPATED_IN]->(e)
        RETURN e.story_time as time, 
               e.chapter_id as chapter, 
               e.description as text, 
               collect(i.name) as characters
        ORDER BY e.story_time ASC
        """
        results = self.conn.query(query)
        
        # Format for the LLM to read easily
        story_log = []
        for r in results:
            log_entry = f"[Time: {r['time']} | Ch: {r['chapter']}] {r['text']} (Characters: {', '.join(r['characters'])})"
            story_log.append(log_entry)
        
        return "\n".join(story_log)

    def get_logic_conflicts(self):
        """Checks for the 'Ghost' error (Dead character acting)."""
        query = """
        MATCH (i:Identity)-[:HAS_STATE]->(s:State)
        WHERE s.status = 'dead'
        WITH i, s
        MATCH (i)-[:PARTICIPATED_IN]->(e:Event)
        WHERE e.story_time > s.story_time
        RETURN i.name as name, s.story_time as death_time, e.story_time as action_time
        """
        results = self.conn.query(query)
        return results if results else []