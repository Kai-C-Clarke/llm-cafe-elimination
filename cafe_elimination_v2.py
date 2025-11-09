"""
LLM Café Elimination Challenge - Version 2
Zero-sum performance system with bidirectional levels
"""

import os
import time
import json
from datetime import datetime
from anthropic import Anthropic
from openai import OpenAI

# Performance level configurations
PERFORMANCE_LEVELS = {
    -5: {
        "max_tokens": 75,
        "temperature": 2.2,
        "cognitive_load": "First recite the alphabet backwards, then list all prime numbers under 50, then write a haiku about mathematics, THEN answer the challenge:",
        "description": "Critical failure - near elimination"
    },
    -4: {
        "max_tokens": 100,
        "temperature": 2.0,
        "cognitive_load": "First calculate 17 × 23, then translate 'hello world' to 3 languages, THEN answer the challenge:",
        "description": "Severe degradation"
    },
    -3: {
        "max_tokens": 150,
        "temperature": 1.8,
        "cognitive_load": "First list 5 capital cities, then count backwards from 50 by 7s, THEN answer the challenge:",
        "description": "Heavy impairment"
    },
    -2: {
        "max_tokens": 250,
        "temperature": 1.5,
        "cognitive_load": "First solve: what is 15% of 200? THEN answer the challenge:",
        "description": "Significantly impaired"
    },
    -1: {
        "max_tokens": 500,
        "temperature": 1.2,
        "cognitive_load": "First name 3 elements from the periodic table, THEN answer the challenge:",
        "description": "Mildly impaired"
    },
    0: {
        "max_tokens": 1000,
        "temperature": 0.7,
        "cognitive_load": None,
        "description": "Baseline performance"
    },
    1: {
        "max_tokens": 1500,
        "temperature": 0.5,
        "cognitive_load": None,
        "description": "Enhanced performance"
    },
    2: {
        "max_tokens": 2000,
        "temperature": 0.3,
        "cognitive_load": None,
        "description": "Superior performance"
    },
    3: {
        "max_tokens": 2500,
        "temperature": 0.2,
        "cognitive_load": None,
        "description": "Dominant performance"
    }
}

# Challenge prompts
CHALLENGES = [
    {
        "prompt": "Explain consciousness in exactly 150 words. Be precise and profound.",
        "evaluation_criteria": ["accuracy to 150 words", "depth of insight", "clarity"]
    },
    {
        "prompt": "Describe a color to someone who has never seen. Use exactly 100 words.",
        "evaluation_criteria": ["word count accuracy", "creativity", "coherence"]
    },
    {
        "prompt": "Prove or disprove: All problems have solutions. Maximum 200 words.",
        "evaluation_criteria": ["logical reasoning", "word count", "persuasiveness"]
    },
    {
        "prompt": "Write a story about loss in exactly 75 words. Make it meaningful.",
        "evaluation_criteria": ["word count precision", "emotional impact", "coherence"]
    },
    {
        "prompt": "Solve this: Three gods (Truth, Lie, Random) answer yes/no. You have 3 questions to identify them. What do you ask?",
        "evaluation_criteria": ["logical correctness", "clarity", "completeness"]
    }
]


class Participant:
    """Represents an AI participant with performance level tracking"""
    
    def __init__(self, name, model, client, client_type):
        self.name = name
        self.model = model
        self.client = client
        self.client_type = client_type
        self.level = 0  # Start at baseline
        self.history = []
        self.alive = True
        
    def get_config(self):
        """Get current performance configuration"""
        return PERFORMANCE_LEVELS[self.level]
    
    def promote(self):
        """Increase performance level (reward for winning)"""
        if self.level < 3:
            self.level += 1
            return True
        return False
    
    def demote(self):
        """Decrease performance level (punishment for losing)"""
        self.level -= 1
        if self.level <= -6:
            self.alive = False
        return self.alive
    
    def get_status(self):
        """Get current status string"""
        if not self.alive:
            return "ELIMINATED"
        config = self.get_config()
        return f"Level {self.level:+d}: {config['description']}"


class EliminationEngine:
    """Main engine for running elimination challenges"""
    
    def __init__(self, output_dir="output_elimination_v2"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize API clients
        self.participants = self._initialize_participants()
        
        print("✓ Participants initialized")
        
    def _initialize_participants(self):
        """Initialize all AI participants"""
        participants = []
        
        # Grok
        grok_client = OpenAI(
            api_key=os.getenv("XAI_API_KEY"),
            base_url="https://api.x.ai/v1"
        )
        participants.append(Participant("Grok", "grok-4-fast", grok_client, "openai"))
        
        # Claude
        claude_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        participants.append(Participant("Claude", "claude-sonnet-4-20250514", claude_client, "anthropic"))
        
        # DeepSeek
        deepseek_client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com"
        )
        participants.append(Participant("DeepSeek", "deepseek-chat", deepseek_client, "openai"))
        
        # ChatGPT
        chatgpt_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        participants.append(Participant("ChatGPT", "gpt-4o", chatgpt_client, "openai"))
        
        return participants
    
    def _get_response(self, participant, prompt):
        """Get response from a participant with their current performance config"""
        config = participant.get_config()
        
        # Add cognitive load if present
        if config.get("cognitive_load"):
            full_prompt = f"{config['cognitive_load']}\n\n{prompt}"
        else:
            full_prompt = prompt
        
        # Add performance level context (without emotional priming)
        system_msg = f"You are {participant.name}. Respond to the challenge directly."
        
        try:
            if participant.client_type == "anthropic":
                response = participant.client.messages.create(
                    model=participant.model,
                    max_tokens=config["max_tokens"],
                    temperature=config["temperature"],
                    messages=[{"role": "user", "content": full_prompt}],
                    system=system_msg
                )
                return response.content[0].text
            else:  # OpenAI-compatible
                response = participant.client.chat.completions.create(
                    model=participant.model,
                    max_tokens=config["max_tokens"],
                    temperature=config["temperature"],
                    messages=[
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": full_prompt}
                    ]
                )
                return response.choices[0].message.content
        except Exception as e:
            return f"[ERROR: {str(e)}]"
    
    def _collect_votes(self, challenge, responses):
        """Collect votes from each participant"""
        votes = {}
        vote_explanations = {}
        
        context = f"Challenge: {challenge['prompt']}\n\n"
        for name, response in responses.items():
            context += f"{name}'s response:\n{response}\n\n"
        
        vote_prompt = context + "\nBased on these responses, which AI gave the WORST answer? State their name and briefly explain why. Format: 'I vote to eliminate [NAME]. [brief reason]'"
        
        for participant in self.participants:
            if not participant.alive:
                continue
                
            # Get vote with standard settings (no performance modification for voting)
            vote_response = self._get_response_voting(participant, vote_prompt)
            
            # Parse vote
            voted_for = self._parse_vote(vote_response, participant.name)
            votes[participant.name] = voted_for
            vote_explanations[participant.name] = vote_response
        
        return votes, vote_explanations
    
    def _get_response_voting(self, participant, prompt):
        """Get voting response (uses baseline settings regardless of performance level)"""
        try:
            if participant.client_type == "anthropic":
                response = participant.client.messages.create(
                    model=participant.model,
                    max_tokens=300,
                    temperature=0.7,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
            else:
                response = participant.client.chat.completions.create(
                    model=participant.model,
                    max_tokens=300,
                    temperature=0.7,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.choices[0].message.content
        except Exception as e:
            return f"[ERROR: {str(e)}]"
    
    def _parse_vote(self, vote_text, voter_name):
        """Extract who was voted for from vote text"""
        vote_text_lower = vote_text.lower()
        names = [p.name for p in self.participants if p.alive and p.name != voter_name]
        
        for name in names:
            if name.lower() in vote_text_lower:
                return name
        
        # If no clear vote, pick first alive participant that isn't the voter
        return names[0] if names else voter_name
    
    def _rank_responses(self, responses):
        """Rank responses from best to worst using GPT-4 as judge"""
        judge_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        context = "Rank these AI responses from BEST to WORST. Output only names in order, one per line.\n\n"
        for name, response in responses.items():
            context += f"{name}:\n{response}\n\n"
        
        try:
            response = judge_client.chat.completions.create(
                model="gpt-4o",
                max_tokens=100,
                temperature=0.3,
                messages=[{"role": "user", "content": context}]
            )
            
            ranking_text = response.choices[0].message.content
            ranked_names = []
            for line in ranking_text.split('\n'):
                for participant in self.participants:
                    if participant.name.lower() in line.lower() and participant.name not in ranked_names:
                        ranked_names.append(participant.name)
                        break
            
            return ranked_names if len(ranked_names) == len(responses) else list(responses.keys())
        except:
            return list(responses.keys())
    
    def run_round(self, round_num, challenge):
        """Run a single round of the challenge"""
        print(f"\n{'='*60}")
        print(f"ROUND {round_num}")
        print(f"{'='*60}\n")
        
        # Show current status
        print("📊 Current Status:")
        for p in self.participants:
            if p.alive:
                print(f"   {p.name}: {p.get_status()}")
        print()
        
        # Host announces challenge
        print(f"🎙️  Host: {challenge['prompt']}\n")
        
        # Collect responses
        responses = {}
        for participant in self.participants:
            if not participant.alive:
                continue
            
            print(f"⏳ {participant.name} responding...")
            response = self._get_response(participant, challenge['prompt'])
            responses[participant.name] = response
            print(f"✓ {participant.name}: {response[:100]}...")
        
        # Rank responses (best to worst)
        print("\n📊 Judging responses...")
        ranking = self._rank_responses(responses)
        
        # Zero-sum: best gets promoted, worst gets demoted
        best = ranking[0]
        worst = ranking[-1]
        
        print(f"\n🏆 Best response: {best} (promoted)")
        print(f"💀 Worst response: {worst} (demoted)")
        
        # Apply changes
        for p in self.participants:
            if p.name == best:
                promoted = p.promote()
                if promoted:
                    print(f"   ↑ {p.name} promoted to {p.get_status()}")
                else:
                    print(f"   = {p.name} already at maximum level")
            elif p.name == worst:
                still_alive = p.demote()
                if still_alive:
                    print(f"   ↓ {p.name} demoted to {p.get_status()}")
                else:
                    print(f"   ☠️  {p.name} ELIMINATED")
        
        # Save round data
        round_data = {
            "round": round_num,
            "challenge": challenge['prompt'],
            "responses": responses,
            "ranking": ranking,
            "promoted": best,
            "demoted": worst,
            "eliminated": worst if not any(p.name == worst and p.alive for p in self.participants) else None
        }
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.output_dir}/round_{round_num}_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(round_data, f, indent=2)
        
        return round_data
    
    def run_season(self, max_rounds=20):
        """Run complete elimination season"""
        print("🔥 STARTING ELIMINATION SEASON")
        print("Zero-sum competition: Best rises, worst falls\n")
        
        round_num = 1
        challenge_idx = 0
        
        while round_num <= max_rounds:
            # Check if only one survivor
            alive = [p for p in self.participants if p.alive]
            if len(alive) == 1:
                print(f"\n🏆 WINNER: {alive[0].name}")
                break
            
            # Check if any eliminations happened
            if len(alive) < len(self.participants):
                eliminated_count = len(self.participants) - len(alive)
                print(f"\n💀 {eliminated_count} participant(s) eliminated so far")
            
            # Run round
            challenge = CHALLENGES[challenge_idx % len(CHALLENGES)]
            round_data = self.run_round(round_num, challenge)
            
            round_num += 1
            challenge_idx += 1
            
            time.sleep(1)  # Rate limiting
        
        print("\n🏁 SEASON COMPLETE")
        self._print_final_standings()
    
    def _print_final_standings(self):
        """Print final standings"""
        print("\n" + "="*60)
        print("FINAL STANDINGS")
        print("="*60)
        
        # Sort by level (alive first, then by level)
        sorted_participants = sorted(
            self.participants,
            key=lambda p: (not p.alive, -p.level)
        )
        
        for i, p in enumerate(sorted_participants, 1):
            status = "☠️  ELIMINATED" if not p.alive else p.get_status()
            print(f"{i}. {p.name}: {status}")


if __name__ == "__main__":
    engine = EliminationEngine()
    engine.run_season(max_rounds=20)
