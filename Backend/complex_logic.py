from neo4j import GraphDatabase

class AdvancedValidator:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    # --- FEATURE 1: RELATIONSHIP LOGIC ---
    def update_relationship(self, char1_id, char2_id, new_type, chapter):
        with self.driver.session() as session:
            # 1. Check previous relationship
            query = """
            MATCH (a:Character {id: $c1})-[r:RELATED]->(b:Character {id: $c2})
            RETURN r.type as old_type
            """
            result = session.run(query, c1=char1_id, c2=char2_id)
            record = result.single()

            # RULE: Enemy -> Ally requires an Event
            if record and record["old_type"] == "enemy" and new_type == "ally":
                print(f"⚠️ ALERT: Relationship Jump in Ch {chapter}!")
                print(f"   Reason: {char1_id} & {char2_id} were ENEMIES. They cannot become ALLIES without a 'Reconciliation' event.")
                return "FAIL"

            # Update if valid
            update = """
            MATCH (a:Character {id: $c1}), (b:Character {id: $c2})
            MERGE (a)-[r:RELATED]->(b)
            SET r.type = $new_type, r.last_chapter = $ch
            """
            session.run(update, c1=char1_id, c2=char2_id, new_type=new_type, ch=chapter)
            print(f"✅ Ch {chapter}: Relationship updated to {new_type}.")

    # --- FEATURE 2: KNOWLEDGE CONSISTENCY ---
    def check_knowledge_leak(self, char_id, fact_id, chapter):
        with self.driver.session() as session:
            # Ask: Does the character KNOW this fact?
            query = """
            MATCH (c:Character {id: $cid})-[:KNOWS]->(f:Fact {id: $fid})
            RETURN f
            """
            if not session.run(query, cid=char_id, fid=fact_id).single():
                print(f"⚠️ ALERT: Knowledge Leak in Ch {chapter}!")
                print(f"   Reason: Character {char_id} is discussing Fact '{fact_id}' but hasn't LEARNED it yet.")
                return "FAIL"
            
            print(f"✅ Ch {chapter}: Knowledge valid. Character knows '{fact_id}'.")

    # --- HELPER: SETUP DATA ---
    def setup_world(self):
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n") # Reset for test
            # Create Characters and a Secret Fact
            session.run("CREATE (:Character {id:'C1', name:'Hero'})")
            session.run("CREATE (:Character {id:'C2', name:'Villain'})")
            session.run("CREATE (:Fact {id:'Secret_Weapon_Location', desc:'Hidden in the cave'})")
            # Set initial Enemy relationship
            session.run("""
                MATCH (a:Character {id:'C1'}), (b:Character {id:'C2'})
                CREATE (a)-[:RELATED {type:'enemy'}]->(b)
            """)

# --- EXECUTION ---
validator = AdvancedValidator("bolt://localhost:7687", "neo4j", "password123")
validator.setup_world()

print("\n--- TEST 1: Relationship Logic ---")
# Try to make them Allies instantly (Should FAIL)
validator.update_relationship("C1", "C2", "ally", 5)

print("\n--- TEST 2: Knowledge Logic ---")
# Hero tries to talk about the Secret Weapon (Should FAIL - he doesn't know it)
validator.check_knowledge_leak("C1", "Secret_Weapon_Location", 5)

validator.close()