import os
from neo4j import GraphDatabase

class GraphManager:
    def __init__(self):
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password")
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def save_extracted_entities(self, entities: dict, metadata: dict):
        """
        Saves nodes and relationships.
        Uses a 'Base Entity' approach to ensure relationships are never dropped
        even if the specific Character/Location node wasn't fully defined yet.
        """
        with self.driver.session() as session:
            session.execute_write(self._save_transaction, entities, metadata)

    def _save_transaction(self, tx, entities, metadata):
        mid = metadata.get("manuscript_id")
        # Unique Scene ID based on chunk/paragraph to allow time-travel querying
        scene_id = f"{mid}_p{metadata.get('paragraph')}"
        
        # 1. SCENE NODE (The Anchor)
        tx.run("""
            MERGE (m:Manuscript {id: $mid})
            MERGE (s:Scene {id: $sid})
            SET s.created_at = timestamp()
            MERGE (m)-[:CONTAINS]->(s)
        """, mid=mid, sid=scene_id)

        # 2. CHARACTERS (Specific Label)
        # We use NarrativeEntity as a base label for everything to make matching easier
        for char in entities.get("characters", []):
            tx.run("""
                MERGE (c:NarrativeEntity {name: $name, manuscript_id: $mid})
                SET c:Character, 
                    c.archetype = $archetype, 
                    c.emotion = $emotion,
                    c.goal = $goal
                MERGE (c)-[:APPEARS_IN]->(s:Scene {id: $sid})
            """, 
            name=char['text'], mid=mid, sid=scene_id,
            archetype=char.get('archetype', 'Unknown'),
            emotion=char.get('emotion', 'Neutral'),
            goal=char.get('goal', 'None'))

        # 3. LOCATIONS (Specific Label)
        for loc in entities.get("locations", []):
            tx.run("""
                MERGE (l:NarrativeEntity {name: $name, manuscript_id: $mid})
                SET l:Location, 
                    l.atmosphere = $atmos,
                    l.type = $type
                MERGE (s:Scene {id: $sid})-[:SETTING_IS]->(l)
            """, 
            name=loc['text'], mid=mid, sid=scene_id,
            atmos=loc.get('atmosphere', 'Neutral'),
            type=loc.get('type', 'Place'))

        # 4. RELATIONSHIPS (The Robust Fix)
        # We MERGE the endpoints as 'NarrativeEntity' first. 
        # This guarantees they exist, so the link is ALWAYS created.
        for rel in entities.get("relationships", []):
            rel_type = rel.get("type", "RELATED").upper().replace(" ", "_")
            source = rel.get("source")
            target = rel.get("target")
            context = rel.get("properties", {}).get("context", "")

            # If source or target are empty, skip
            if not source or not target:
                continue

            # Dynamic Cypher injection for relationship type
            query = f"""
                MERGE (a:NarrativeEntity {{name: $source, manuscript_id: $mid}})
                MERGE (b:NarrativeEntity {{name: $target, manuscript_id: $mid}})
                MERGE (a)-[r:{rel_type}]->(b)
                SET r.context = $context, 
                    r.last_seen_in = $sid,
                    r.strength = 'High'
            """
            tx.run(query, mid=mid, sid=scene_id, source=source, target=target, context=context)

        print(f"💾 Graph Saved: {len(entities.get('characters', []))} Nodes, {len(entities.get('relationships', []))} Relationships.")

graph_db = GraphManager()