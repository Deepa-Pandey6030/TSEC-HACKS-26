import os
import json
import re
from typing import List, TypedDict, Annotated, Dict, Any
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv

load_dotenv()

class GraphState(TypedDict):
    text: str
    metadata: Dict[str, Any]
    entities: Annotated[Dict[str, Any], lambda old, new: new]
    active_characters: List[str]

class EntityExtractor:
    def __init__(self):
        # 1. LIMIT TOKENS: Prevents runaways and timeouts
        self.llm = ChatGroq(
            temperature=0.1,  
            model_name="llama-3.1-8b-instant", 
            groq_api_key=os.getenv("GROQ_API_KEY"),
            max_tokens=4000 
        )
        self.workflow = self._build_workflow()

    def _surgical_json_parser(self, text: str):
        """
        CRITICAL FIX: Manually extracts the first valid JSON object.
        Ignores 'Extra data' errors by stopping exactly at the closing brace.
        """
        text = text.strip()
        start_idx = text.find('{')
        if start_idx == -1:
            return None
            
        balance = 0
        in_string = False
        escape = False
        
        # Scan character by character from the first '{'
        for i in range(start_idx, len(text)):
            char = text[i]
            
            # Handle string boundaries (ignore braces inside strings)
            if char == '"' and not escape:
                in_string = not in_string
            
            if char == '\\' and not escape:
                escape = True
            else:
                escape = False
                
            if not in_string:
                if char == '{':
                    balance += 1
                elif char == '}':
                    balance -= 1
                    
                    # If balance is zero, we found the EXACT end of the JSON
                    if balance == 0:
                        clean_json = text[start_idx : i + 1]
                        try:
                            return json.loads(clean_json)
                        except json.JSONDecodeError:
                            # If parsing fails, it might be a fluke, keep looking
                            continue
        return None

    def _extract_entities_node(self, state: GraphState):
        # 2. SAFETY SLICE: Keep input under 6k chars to avoid 413 Errors
        safe_text = state["text"][:6000]
        
        prompt = ChatPromptTemplate.from_template("""
            Analyze the text and extract the Narrative Graph.
            
            ACTIVE MEMORY: {active_characters}
            
            STRICT RULES:
            1. Output JSON ONLY. No intro, no outro, no markdown.
            2. Keys must be in "double quotes".
            3. "source" and "target" in relationships must match "characters" names EXACTLY.
            
            JSON STRUCTURE:
            {{
                "characters": [
                    {{ "text": "Name", "archetype": "Role", "goal": "Goal" }}
                ],
                "locations": [
                    {{ "text": "Place Name", "type": "Setting" }}
                ],
                "relationships": [
                    {{ "source": "Name", "target": "Name", "type": "VERB", "properties": {{ "context": "Reason" }} }}
                ]
            }}
            
            TEXT:
            {text}
        """)
        
        try:
            # Invoke AI
            response = self.llm.invoke(prompt.format(
                text=safe_text, 
                active_characters=state["active_characters"]
            ))
            
            # 3. USE SURGICAL PARSER
            extracted = self._surgical_json_parser(response.content)
            
            if not extracted:
                # Fallback: Try a greedy regex if surgical fails (rare)
                json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
                if json_match:
                    try:
                        extracted = json.loads(json_match.group())
                    except:
                        raise ValueError("Could not parse JSON even with fallback.")
                else:
                    raise ValueError("No JSON found in response.")
            
            # 4. Update Memory
            new_chars = [c.get('text') for c in extracted.get('characters', [])]
            updated_memory = list(set(state["active_characters"] + new_chars))[-15:] 

            return {"entities": extracted, "active_characters": updated_memory}
            
        except Exception as e:
            print(f"⚠️ Extraction Skipped (Chunk Error): {e}")
            # Return empty structure so the loop continues instead of crashing
            return {
                "entities": {"characters": [], "locations": [], "relationships": []},
                "active_characters": state["active_characters"]
            }

    def _build_workflow(self):
        builder = StateGraph(GraphState)
        builder.add_node("extract", self._extract_entities_node)
        builder.set_entry_point("extract")
        builder.add_edge("extract", END)
        return builder.compile()

    async def extract(self, text: str, metadata: dict, context: list = None):
        return (await self.workflow.ainvoke({
            "text": text, "metadata": metadata, 
            "entities": {}, "active_characters": context or []
        }))["entities"]