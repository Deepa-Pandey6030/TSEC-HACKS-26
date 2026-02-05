from crewai import Agent, LLM
from config.settings import AGENT_CONFIG, GROQ_MODEL, GROQ_API_KEY
from tools import EmotionAnalyzer, CharacterTraitExtractor
import os


def get_llm():
    """Get the configured LLM - Using Groq only"""
    # Set GROQ_API_KEY environment variable
    if GROQ_API_KEY:
        os.environ["GROQ_API_KEY"] = GROQ_API_KEY
    
    print(f"🤖 Using Groq LLM with model: {GROQ_MODEL}")
    return LLM(model=GROQ_MODEL, temperature=0.7)


class CharacterVoiceAgents:
    """Factory class for creating character voice agents"""
    
    def __init__(self):
        self.llm = get_llm()
    
    def character_analyzer_agent(self) -> Agent:
        """Creates the character behavior analyst agent"""
        config = AGENT_CONFIG["character_analyzer"]
        
        return Agent(
            role=config["role"],
            goal=config["goal"],
            backstory=config["backstory"],
            verbose=config["verbose"],
            allow_delegation=config["allow_delegation"],
            llm=self.llm,
            tools=[CharacterTraitExtractor(), EmotionAnalyzer()]
        )
    
    def voice_profile_creator_agent(self) -> Agent:
        """Creates the voice profile designer agent"""
        config = AGENT_CONFIG["voice_profile_creator"]
        
        return Agent(
            role=config["role"],
            goal=config["goal"],
            backstory=config["backstory"],
            verbose=config["verbose"],
            allow_delegation=config["allow_delegation"],
            llm=self.llm
        )
    
    def scene_voice_director_agent(self) -> Agent:
        """Creates the scene-based voice director agent"""
        config = AGENT_CONFIG["scene_voice_director"]
        
        return Agent(
            role=config["role"],
            goal=config["goal"],
            backstory=config["backstory"],
            verbose=config["verbose"],
            allow_delegation=config["allow_delegation"],
            llm=self.llm,
            tools=[EmotionAnalyzer()]
        )
