from crewai import Crew, Process
from agents import CharacterVoiceAgents
from tasks import CharacterVoiceTasks
import json
from datetime import datetime
from pathlib import Path


class CharacterVoiceCrew:
    """Main crew orchestration for character voice analysis and generation"""
    
    def __init__(self):
        self.agents_factory = CharacterVoiceAgents()
        self.output_dir = Path("outputs")
        self.output_dir.mkdir(exist_ok=True)
    
    def create_agents(self):
        """Create all required agents"""
        return {
            'character_analyzer': self.agents_factory.character_analyzer_agent(),
            'voice_profile_creator': self.agents_factory.voice_profile_creator_agent(),
            'scene_voice_director': self.agents_factory.scene_voice_director_agent()
        }
    
    def analyze_character(self, summary: str, character_name: str, 
                         scene_description: str = None, save_output: bool = True):
        """
        Main method to analyze character and create voice profile
        
        Args:
            summary: Character description/story summary
            character_name: Name of the character
            scene_description: Optional scene for specific voice direction
            save_output: Whether to save output to file
        
        Returns:
            dict: Complete analysis and voice profile
        """
        
        print(f"\n{'='*80}")
        print(f"Starting Character Voice Analysis for: {character_name}")
        print(f"{'='*80}\n")
        
        # Create agents
        agents = self.create_agents()
        
        # Create tasks
        tasks = CharacterVoiceTasks.create_task_sequence(
            agents=agents,
            summary=summary,
            character_name=character_name,
            scene_description=scene_description
        )
        
        # Determine which agents to use based on tasks
        active_agents = [agents['character_analyzer'], agents['voice_profile_creator']]
        if scene_description:
            active_agents.append(agents['scene_voice_director'])
        
        # Create and run crew
        crew = Crew(
            agents=active_agents,
            tasks=tasks,
            process=Process.sequential,
            verbose=True
        )
        
        print("\n🚀 Executing crew tasks...\n")
        result = crew.kickoff()
        
        print(f"\n{'='*80}")
        print("✅ Analysis Complete!")
        print(f"{'='*80}\n")
        
        # Process and save results
        if save_output:
            self._save_results(character_name, result, scene_description)
        
        return result
    
    def _save_results(self, character_name: str, result, scene_description: str = None):
        """Save results to JSON file"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{character_name.lower().replace(' ', '_')}_{timestamp}"
        
        if scene_description:
            filename += "_with_scene"
        
        filepath = self.output_dir / f"{filename}.json"
        
        # Structure the output
        output_data = {
            "character_name": character_name,
            "timestamp": timestamp,
            "analysis": str(result),
            "has_scene_direction": scene_description is not None
        }
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Results saved to: {filepath}")
        
        # Also save a readable text version
        text_filepath = self.output_dir / f"{filename}.txt"
        with open(text_filepath, 'w', encoding='utf-8') as f:
            f.write(f"Character Voice Analysis for: {character_name}\n")
            f.write(f"Generated: {timestamp}\n")
            f.write("="*80 + "\n\n")
            f.write(str(result))
        
        print(f"📄 Readable version saved to: {text_filepath}")
    
    def quick_profile(self, summary: str, character_name: str):
        """Quick character profile without scene direction"""
        return self.analyze_character(summary, character_name, scene_description=None)
    
    def full_profile_with_scene(self, summary: str, character_name: str, scene: str):
        """Full profile including scene-specific direction"""
        return self.analyze_character(summary, character_name, scene_description=scene)


if __name__ == "__main__":
    # Example usage
    crew = CharacterVoiceCrew()
    
    example_summary = """
    Maya is the cheerful protagonist of our romantic comedy. She's incredibly bubbly 
    and energetic, with an infectious laugh that lights up every room. She's naturally 
    playful and slightly mischievous, always finding ways to tease her friends in a 
    loving way. Maya speaks very quickly when she's excited (which is often), and has 
    a habit of elongating her words for dramatic effect - "That's amaaaazing!" She 
    giggles frequently, sometimes mid-sentence, and her voice rises in pitch when 
    she's being particularly playful. Despite her generally upbeat nature, she becomes 
    surprisingly soft-spoken and gentle during heartfelt moments, showing her emotional 
    depth. She's in her mid-20s, optimistic, and approaches life with childlike wonder.
    """
    
    example_scene = """
    Maya just walked into her apartment to find all her friends have thrown her a 
    surprise birthday party. She's completely shocked, standing frozen in the doorway 
    with her hand over her mouth. Then her eyes start to well up with happy tears as 
    the reality sinks in. She lets out a little squeal of delight before bursting into 
    laughter mixed with emotional crying, then rushes to hug her best friend.
    """
    
    result = crew.full_profile_with_scene(
        summary=example_summary,
        character_name="Maya",
        scene=example_scene
    )
