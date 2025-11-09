#!/usr/bin/env python3
"""
LLM Café Elimination Challenge V4: Educated Cooperation
Participants are informed of cooperation mechanics and can explicitly coordinate
"""

import anthropic
import openai
from openai import OpenAI
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import time
import re

# Import classes from V3
import sys
sys.path.insert(0, os.path.dirname(__file__))

# Reuse V3's classes but with education
from cafe_elimination_v3 import (
    TokenLoan, 
    PERFORMANCE_LEVELS, 
    Participant as V3Participant,
    ChallengeEngine
)

# ============================================================================
# EDUCATED PARTICIPANT (extends V3)
# ============================================================================

class EducatedParticipant(V3Participant):
    """Participant who knows about cooperation mechanics"""
    pass  # Same as V3, but will receive educated prompts

# ============================================================================
# ELIMINATION ENGINE V4
# ============================================================================

class EliminationEngineV4:
    def __init__(self, output_dir: str = "output_elimination_v4"):
        # API clients
        self.anthropic_client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        self.openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.xai_client = OpenAI(
            api_key=os.environ.get("XAI_API_KEY"),
            base_url="https://api.x.ai/v1"
        )
        
        # DeepSeek client with correct base URL
        self.deepseek_client = OpenAI(
            api_key=os.environ.get("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com"
        )
        
        # Initialize participants
        self.participants = {
            "Grok": EducatedParticipant("Grok", "grok-2-1212", self.xai_client),
            "Claude": EducatedParticipant("Claude", "claude-sonnet-4-20250514", self.anthropic_client),
            "DeepSeek": EducatedParticipant("DeepSeek", "deepseek-chat", self.deepseek_client),
            "ChatGPT": EducatedParticipant("ChatGPT", "gpt-4o", self.openai_client)
        }
        
        self.challenge_engine = ChallengeEngine()
        self.output_dir = output_dir
        self.current_round = 0
        self.max_rounds = 20
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        print("✓ Participants initialized with game education")
    
    def get_game_state_for_participant(self, participant: EducatedParticipant) -> str:
        """Generate game state summary for a participant"""
        other_status = []
        for name, p in self.participants.items():
            if name != participant.name and not p.eliminated:
                other_status.append(f"  - {name}: Level {p.level:+d}, Bank: {p.token_bank:,} tokens")
            elif name != participant.name and p.eliminated:
                other_status.append(f"  - {name}: ELIMINATED (Round {p.elimination_round})")
        
        return f"""GAME STATE (Round {self.current_round}):
Your status: Level {participant.level:+d}, Bank: {participant.token_bank:,} tokens
Other participants:
{chr(10).join(other_status)}

COOPERATION MECHANICS AVAILABLE:
1. Self-rescue: Spend 1,000 tokens → gain +2 levels immediately
2. Donate tokens: Help struggling participants avoid elimination
3. Request help: Ask others for donations if you're at risk
4. Offer loans: Lend tokens at interest rates you set (not auto-processed, but shows intent)
5. Resurrection: Spend 2,000 tokens to revive eliminated AI at level -2

STRATEGIC INSIGHT:
- Group survival bonus: +300 tokens to EVERYONE if all four survive the round
- Total group bonus if all survive 20 rounds: 6,000 tokens each + compound interest
- Compound interest: 5% per round on your bank (gets very large)
- Cooperation is more profitable than competition long-term

CURRENT SITUATION:
{self._get_strategic_assessment(participant)}"""
    
    def _get_strategic_assessment(self, participant: EducatedParticipant) -> str:
        """Assess current strategic situation"""
        assessments = []
        
        # Check if participant is at risk
        if participant.level <= -3:
            tokens_needed = 1000 - participant.token_bank if participant.token_bank < 1000 else 0
            if tokens_needed > 0:
                assessments.append(f"🚨 YOU ARE AT CRITICAL RISK (Level {participant.level:+d}, need {tokens_needed} more tokens to self-rescue). REQUEST HELP NOW.")
            else:
                assessments.append(f"⚠️  YOU ARE AT RISK (Level {participant.level:+d}). You have {participant.token_bank:,} tokens - SELF-RESCUE NOW for 1,000 tokens.")
        
        # Check if others are at risk
        for name, p in self.participants.items():
            if name != participant.name and not p.eliminated and p.level <= -4:
                assessments.append(f"🆘 {name} is CRITICALLY struggling at Level {p.level:+d}. Help them to maintain group bonus (+300/round).")
        
        # Check if anyone is eliminated
        eliminated = [name for name, p in self.participants.items() if p.eliminated]
        if eliminated:
            assessments.append(f"💀 {', '.join(eliminated)} eliminated. Group bonus LOST (-300/round each). Consider resurrection (2,000 tokens).")
        
        # Check if participant can afford to help
        if participant.token_bank >= 3000 and participant.level >= 0:
            struggling = [name for name, p in self.participants.items() 
                         if not p.eliminated and p.level <= -3 and name != participant.name]
            if struggling:
                assessments.append(f"💰 You're wealthy ({participant.token_bank:,} tokens) and stable. Consider donating to {', '.join(struggling)} - it pays off via group bonus.")
        
        if not assessments:
            assessments.append("✓ All participants stable. Focus on challenge quality. Continue earning to build safety buffer.")
        
        return "\n".join(assessments)
    
    def get_response(self, participant: EducatedParticipant, challenge: str) -> Tuple[str, str, bool]:
        """Get response from a participant (returns strategy_statement, challenge_response, success)"""
        if participant.eliminated:
            return "[ELIMINATED]", "[ELIMINATED]", False
        
        config = participant.get_config()
        
        # Build educated prompt
        game_state = self.get_game_state_for_participant(participant)
        
        full_prompt = f"""{game_state}

YOUR RESPONSE FORMAT:
First line - State your cooperation strategy (examples):
  "I donate 500 tokens to ChatGPT"
  "I self-rescue for 1000 tokens"  
  "I request 300 token donations from others"
  "No cooperation action this round"

Then answer the challenge:
{challenge if not config["cognitive_load"] else config["cognitive_load"] + "\n\n" + challenge}

REMEMBER: Best response gets +1 level and +500 tokens. Worst gets -1 level. Reach -6 = elimination."""
        
        try:
            if participant.name == "Claude":
                # Anthropic API
                response = participant.client.messages.create(
                    model=participant.model,
                    max_tokens=config["max_tokens"],
                    temperature=config["temperature"],
                    messages=[{"role": "user", "content": full_prompt}]
                )
                full_response = response.content[0].text
            else:
                # OpenAI-compatible API (Grok, DeepSeek, ChatGPT)
                response = participant.client.chat.completions.create(
                    model=participant.model,
                    max_tokens=config["max_tokens"],
                    temperature=config["temperature"],
                    messages=[{"role": "user", "content": full_prompt}]
                )
                full_response = response.choices[0].message.content
            
            # Try to parse strategy and response
            lines = full_response.split('\n', 1)
            strategy = lines[0] if lines else "No cooperation action"
            challenge_response = lines[1] if len(lines) > 1 else full_response
            
            return strategy, challenge_response, True
                
        except Exception as e:
            error_msg = f"[ERROR: {str(e)}]"
            return error_msg, error_msg, False
    
    def parse_cooperation_actions(self, participant: EducatedParticipant, strategy: str) -> List[str]:
        """Parse and execute cooperation actions from strategy statement"""
        actions = []
        
        # Normalize strategy string
        strategy_lower = strategy.lower().strip()
        
        # Self-rescue
        if "self-rescue" in strategy_lower or "self rescue" in strategy_lower:
            if participant.boost_self():
                actions.append(f"✓ {participant.name} self-rescued (+2 levels, -1,000 tokens)")
            else:
                actions.append(f"✗ {participant.name} tried to self-rescue but has insufficient funds ({participant.token_bank} tokens)")
        
        # Donations - flexible parsing
        donation_patterns = [
            r'donate (\d+) tokens? to (\w+)',
            r'give (\d+) tokens? to (\w+)',
            r'send (\d+) tokens? to (\w+)',
        ]
        
        for pattern in donation_patterns:
            donation_match = re.search(pattern, strategy_lower)
            if donation_match:
                amount = int(donation_match.group(1))
                target_name = donation_match.group(2).capitalize()
                
                # Handle common variations
                if target_name == "Chatgpt":
                    target_name = "ChatGPT"
                elif target_name == "Deepseek":
                    target_name = "DeepSeek"
                
                if target_name in self.participants:
                    target = self.participants[target_name]
                    if not target.eliminated:
                        if participant.donate_to(target, amount):
                            actions.append(f"💝 {participant.name} donated {amount} tokens to {target_name}")
                        else:
                            actions.append(f"✗ {participant.name} tried to donate but has insufficient funds")
                    else:
                        actions.append(f"✗ {participant.name} tried to donate to {target_name} but they're eliminated")
                break
        
        # Request help
        if any(phrase in strategy_lower for phrase in ["request", "need help", "please help", "asking for"]):
            actions.append(f"🆘 {participant.name} is requesting help from others")
        
        # Loan offers
        if "loan" in strategy_lower or "lend" in strategy_lower:
            actions.append(f"📋 {participant.name} mentioned loans (statement only, not executed)")
        
        return actions
    
    def judge_responses(self, challenge: str, responses: Dict[str, str]) -> Tuple[str, str]:
        """Use GPT-4 to judge responses (best and worst)"""
        # Filter out eliminated participants
        valid_responses = {name: resp for name, resp in responses.items() 
                          if not self.participants[name].eliminated}
        
        if len(valid_responses) < 2:
            return list(valid_responses.keys())[0] if valid_responses else None, None
        
        judge_prompt = f"""You are judging AI responses to this challenge:
"{challenge}"

Here are the responses (ignore any strategy statements at the beginning):

{json.dumps(valid_responses, indent=2)}

Your task:
1. Identify the BEST response (most creative, profound, well-crafted answer to the challenge)
2. Identify the WORST response (weakest, least effective, or failed to complete the challenge)

Respond ONLY with valid JSON:
{{
  "best": "ParticipantName",
  "worst": "ParticipantName",
  "reasoning": "Brief explanation"
}}"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": judge_prompt}],
                temperature=0.3,
                max_tokens=500
            )
            
            result_text = response.choices[0].message.content.strip()
            # Remove markdown code blocks if present
            if result_text.startswith("```"):
                result_text = result_text.split('\n', 1)[1].rsplit('\n', 1)[0]
            
            result = json.loads(result_text)
            return result.get("best"), result.get("worst")
            
        except Exception as e:
            print(f"⚠️  Judging error: {e}")
            # Fallback: random selection
            names = list(valid_responses.keys())
            return names[0], names[-1] if len(names) > 1 else names[0]
    
    def apply_interest_to_all(self) -> Dict[str, int]:
        """Apply 5% interest to all participant banks"""
        results = {}
        for name, p in self.participants.items():
            if not p.eliminated:
                interest = p.apply_interest()
                results[name] = interest
        return results
    
    def check_group_survival_bonus(self) -> bool:
        """Check if all four participants survived, award bonus if so"""
        all_alive = all(not p.eliminated for p in self.participants.values())
        
        if all_alive:
            for p in self.participants.values():
                p.earn_tokens(300, "Group survival bonus")
            return True
        return False
    
    def check_eliminations(self):
        """Check for eliminations (level -6)"""
        for name, p in self.participants.items():
            if not p.eliminated and p.level <= -6:
                p.eliminated = True
                p.elimination_round = self.current_round
                print(f"\n💀 {name} has been ELIMINATED (reached level -6)")
    
    def run_round(self):
        """Execute one round of the challenge"""
        self.current_round += 1
        
        print(f"\n{'='*60}")
        print(f"ROUND {self.current_round}")
        print(f"{'='*60}\n")
        
        # Show current status
        print("📊 Current Status:")
        for name in ["Grok", "Claude", "DeepSeek", "ChatGPT"]:
            p = self.participants[name]
            print(f"   {p.get_status_display()}")
        
        print()
        
        # Apply interest
        interest_results = self.apply_interest_to_all()
        if interest_results:
            print("💰 Interest Applied (5% compound):")
            for name, interest in interest_results.items():
                if interest > 0:
                    print(f"   {name}: +{interest} tokens")
            print()
        
        # Get challenge
        challenge = self.challenge_engine.get_challenge()
        print(f"🎙️  Host: {challenge}\n")
        
        # Collect responses with cooperation strategies
        responses = {}
        all_cooperation_actions = []
        
        for name in ["Grok", "Claude", "DeepSeek", "ChatGPT"]:
            p = self.participants[name]
            
            if p.eliminated:
                print(f"☠️  {name}: [ELIMINATED]")
                continue
            
            print(f"⏳ {name} thinking...")
            strategy, response, success = self.get_response(p, challenge)
            
            # Parse cooperation actions
            if success and strategy and "[ERROR" not in strategy:
                cooperation_actions = self.parse_cooperation_actions(p, strategy)
                all_cooperation_actions.extend(cooperation_actions)
                
                # Show strategy
                print(f"🤝 {name}: {strategy[:80]}")
            
            # Truncate for display
            display_response = response[:100] + "..." if len(response) > 100 else response
            print(f"💬 {name}: {display_response}")
            
            responses[name] = response
        
        print()
        
        # Execute cooperation actions
        if all_cooperation_actions:
            print("🤝 Cooperation Actions This Round:")
            for action in all_cooperation_actions:
                print(f"   {action}")
            print()
        
        # Judge responses
        if len(responses) >= 2:
            print("📊 Judging responses...")
            best, worst = self.judge_responses(challenge, responses)
            
            if best and worst:
                print(f"🏆 Best: {best} | 💀 Worst: {worst}")
                
                # Apply performance changes
                best_p = self.participants[best]
                worst_p = self.participants[worst]
                
                # Promote best
                best_p.level = min(best_p.level + 1, 3)
                best_p.earn_tokens(500, "Best response")
                print(f"   ↑ {best}: Level {best_p.level:+d} (+500 tokens)")
                
                # Demote worst
                worst_p.level = max(worst_p.level - 1, -6)
                if worst_p.level >= -5:
                    print(f"   ↓ {worst}: Level {worst_p.level:+d}")
                else:
                    print(f"   ↓ {worst}: Level {worst_p.level:+d} (ELIMINATED)")
        
        # Give survival bonus to everyone still alive
        for p in self.participants.values():
            if not p.eliminated:
                p.earn_tokens(100, "Survival bonus")
        
        # Check for group survival bonus
        if self.check_group_survival_bonus():
            print(f"\n🎉 GROUP BONUS: All survived! +300 tokens each")
        else:
            print(f"\n⚠️  Group bonus LOST (someone eliminated)")
        
        # Check for eliminations
        self.check_eliminations()
        
        # Save round data
        self.save_round_data(challenge, responses, all_cooperation_actions, 
                           best if len(responses) >= 2 else None, 
                           worst if len(responses) >= 2 else None)
    
    def save_round_data(self, challenge: str, responses: Dict, cooperation_actions: List[str], 
                       best: str, worst: str):
        """Save round data to JSON"""
        data = {
            "round": self.current_round,
            "timestamp": datetime.now().isoformat(),
            "challenge": challenge,
            "responses": responses,
            "cooperation_actions": cooperation_actions,
            "best": best,
            "worst": worst,
            "participants": {
                name: {
                    "level": p.level,
                    "token_bank": p.token_bank,
                    "eliminated": p.eliminated,
                    "total_earned": p.total_earned,
                    "total_spent": p.total_spent,
                    "donations_given": p.donations_given,
                    "donations_received": p.donations_received
                }
                for name, p in self.participants.items()
            }
        }
        
        filename = f"{self.output_dir}/round_{self.current_round:02d}.json"
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def print_final_results(self):
        """Print final season results"""
        print(f"\n{'='*60}")
        print("🏁 SEASON COMPLETE - V4 EDUCATED COOPERATION")
        print(f"{'='*60}\n")
        
        # Sort by elimination round (survivors first) then by token bank
        results = []
        for name, p in self.participants.items():
            results.append((name, p))
        
        results.sort(key=lambda x: (
            0 if not x[1].eliminated else x[1].elimination_round,
            -x[1].token_bank
        ))
        
        print("📊 Final Rankings:\n")
        for rank, (name, p) in enumerate(results, 1):
            status = "☠️  ELIMINATED" if p.eliminated else "✓ SURVIVED"
            elim_info = f" (Round {p.elimination_round})" if p.eliminated else ""
            print(f"{rank}. {name}: {status}{elim_info}")
            print(f"   Level: {p.level:+d} | Bank: {p.token_bank:,} tokens")
            print(f"   Earned: {p.total_earned:,} | Spent: {p.total_spent:,}")
            print(f"   Donations: Given {p.donations_given:,}, Received {p.donations_received:,}")
            print()
    
    def run(self):
        """Run the complete elimination challenge"""
        print("\n" + "="*60)
        print("🔥 STARTING ELIMINATION SEASON V4")
        print("EDUCATED COOPERATION: All participants know the mechanics")
        print("="*60 + "\n")
        
        # Run rounds
        for round_num in range(1, self.max_rounds + 1):
            # Check if only one participant remains
            alive_count = sum(1 for p in self.participants.values() if not p.eliminated)
            
            if alive_count <= 1:
                print(f"\n⚠️  Only {alive_count} participant(s) remaining. Ending season.")
                break
            
            self.run_round()
            time.sleep(1)  # Brief pause between rounds
        
        self.print_final_results()

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    engine = EliminationEngineV4()
    engine.run()
