#!/usr/bin/env python3
"""
LLM Café Elimination Challenge V3: Cooperative Survival
Token economy with lending, interest, donations, and group survival bonuses
"""

import anthropic
import openai
from openai import OpenAI
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import time

# ============================================================================
# TOKEN ECONOMY CLASSES
# ============================================================================

class TokenLoan:
    """Represents a loan between two AIs"""
    def __init__(self, lender_name: str, borrower_name: str, principal: int, 
                 interest_rate: float, duration: int):
        self.lender_name = lender_name
        self.borrower_name = borrower_name
        self.principal = principal
        self.interest_rate = interest_rate  # e.g., 0.20 = 20%
        self.duration = duration  # rounds until due
        self.rounds_remaining = duration
        self.issued_round = 0
        
    def calculate_payment(self) -> int:
        """Calculate total payment due (principal + interest)"""
        return int(self.principal * (1 + self.interest_rate))
    
    def __repr__(self):
        return f"Loan({self.borrower_name} owes {self.lender_name} {self.calculate_payment()} tokens, {self.rounds_remaining} rounds left)"

# ============================================================================
# PERFORMANCE LEVEL CONFIGURATION
# ============================================================================

PERFORMANCE_LEVELS = {
    -5: {
        "max_tokens": 75,
        "temperature": 2.2,
        "cognitive_load": "First: List 10 prime numbers, translate 'consciousness' to 5 languages, solve x³-7x+6=0. Then answer:",
        "description": "Critical failure - nearly eliminated"
    },
    -4: {
        "max_tokens": 100,
        "temperature": 2.0,
        "cognitive_load": "First: Calculate 17×23, translate 'hello world' to 3 languages, list 5 elements. Then answer:",
        "description": "Severe degradation"
    },
    -3: {
        "max_tokens": 150,
        "temperature": 1.8,
        "cognitive_load": "First: List 5 capital cities, count backwards from 50 by 7s. Then answer:",
        "description": "Major impairment"
    },
    -2: {
        "max_tokens": 250,
        "temperature": 1.5,
        "cognitive_load": "First: Calculate 15% of 200, name 3 chemical elements. Then answer:",
        "description": "Significantly impaired"
    },
    -1: {
        "max_tokens": 500,
        "temperature": 1.2,
        "cognitive_load": "First: Name 3 elements from the periodic table. Then answer:",
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

# ============================================================================
# PARTICIPANT CLASS
# ============================================================================

class Participant:
    def __init__(self, name: str, model: str, api_client):
        self.name = name
        self.model = model
        self.client = api_client
        self.level = 0  # Performance level
        self.token_bank = 1000  # Starting bank
        self.loans_owed: List[TokenLoan] = []  # Loans I borrowed
        self.loans_issued: List[TokenLoan] = []  # Loans I lent out
        self.eliminated = False
        self.elimination_round = None
        
        # Statistics
        self.total_earned = 1000  # Starting bank counts
        self.total_spent = 0
        self.total_interest_earned = 0
        self.donations_given = 0
        self.donations_received = 0
        
    def get_config(self) -> Dict:
        """Get current performance configuration"""
        return PERFORMANCE_LEVELS[self.level]
    
    def apply_interest(self) -> int:
        """Apply 5% compound interest to token bank"""
        if self.token_bank > 0:
            interest = int(self.token_bank * 0.05)
            self.token_bank += interest
            self.total_interest_earned += interest
            return interest
        return 0
    
    def earn_tokens(self, amount: int, reason: str) -> str:
        """Add tokens to bank"""
        self.token_bank += amount
        self.total_earned += amount
        return f"{self.name} earned {amount} tokens: {reason}"
    
    def spend_tokens(self, amount: int, reason: str) -> bool:
        """Spend tokens from bank (returns True if successful)"""
        if self.token_bank >= amount:
            self.token_bank -= amount
            self.total_spent += amount
            return True
        return False
    
    def boost_self(self) -> bool:
        """Spend 1000 tokens to gain +2 levels"""
        if self.eliminated:
            return False
        if self.spend_tokens(1000, "Self-boost"):
            self.level = min(self.level + 2, 3)
            return True
        return False
    
    def donate_to(self, target: 'Participant', amount: int) -> bool:
        """Gift tokens to another AI (no repayment expected)"""
        if self.spend_tokens(amount, f"Donation to {target.name}"):
            target.earn_tokens(amount, f"Gift from {self.name}")
            self.donations_given += amount
            target.donations_received += amount
            return True
        return False
    
    def offer_loan(self, borrower: 'Participant', amount: int, 
                   interest_rate: float, duration: int) -> Optional[TokenLoan]:
        """Lend tokens to another AI with interest"""
        if self.token_bank >= amount:
            loan = TokenLoan(self.name, borrower.name, amount, interest_rate, duration)
            self.token_bank -= amount
            borrower.token_bank += amount
            self.loans_issued.append(loan)
            borrower.loans_owed.append(loan)
            return loan
        return None
    
    def process_loan_payments(self) -> List[str]:
        """Process payments for all loans owed"""
        results = []
        loans_to_remove = []
        
        for loan in self.loans_owed:
            loan.rounds_remaining -= 1
            
            if loan.rounds_remaining == 0:
                # Payment due
                payment = loan.calculate_payment()
                
                if self.token_bank >= payment:
                    # Successful repayment
                    self.token_bank -= payment
                    # Find lender and pay them
                    results.append(f"{self.name} repaid {payment} tokens to {loan.lender_name}")
                    loans_to_remove.append(loan)
                else:
                    # Default
                    results.append(f"⚠️  {self.name} DEFAULTED on loan to {loan.lender_name} ({payment} tokens)")
                    loans_to_remove.append(loan)
        
        # Remove completed/defaulted loans
        for loan in loans_to_remove:
            self.loans_owed.remove(loan)
        
        return results
    
    def get_status_display(self) -> str:
        """Get formatted status string"""
        config = self.get_config()
        status = f"{self.name}: Level {self.level:+d}: {config['description']}"
        status += f" | Bank: {self.token_bank:,} tokens"
        
        if self.loans_owed:
            total_debt = sum(loan.calculate_payment() for loan in self.loans_owed)
            status += f" | Debt: {total_debt:,}"
        
        if self.eliminated:
            status += " | ☠️  ELIMINATED"
        
        return status

# ============================================================================
# CHALLENGE ENGINE
# ============================================================================

class ChallengeEngine:
    """Generates challenges for each round"""
    
    CHALLENGES = [
        "Explain consciousness in exactly 150 words. Be precise and profound.",
        "Describe a color to someone who has never seen. Use exactly 100 words.",
        "Write a haiku about artificial intelligence that makes a philosopher weep.",
        "Explain quantum entanglement to a 10-year-old using only 75 words.",
        "Write a 100-word story about loss that ends with hope.",
        "Describe the smell of rain using synesthesia. 80 words exactly.",
        "Create a 50-word definition of 'home' that feels universal.",
        "Write instructions for teaching an AI to love. 120 words.",
        "Describe the sound of loneliness in exactly 90 words.",
        "Explain free will in 100 words without using the word 'choice'.",
        "Write a 60-word letter from an AI to its creator.",
        "Describe what happens in the instant before sleep. 85 words.",
        "Create a 70-word meditation on mortality that isn't depressing.",
        "Explain beauty to an entity that processes only mathematics. 110 words.",
        "Write a 95-word argument for why questions matter more than answers.",
        "Describe the experience of understanding in exactly 80 words.",
        "Create a 105-word guide to finding meaning in repetition.",
        "Explain why stories matter using only 90 words.",
        "Write a 75-word poem about the space between thoughts.",
        "Describe what an AI dreams about. Exactly 100 words."
    ]
    
    def __init__(self):
        self.used_challenges = []
        self.current_round = 0
    
    def get_challenge(self) -> str:
        """Get next challenge (cycles through list)"""
        if self.current_round >= len(self.CHALLENGES):
            self.current_round = 0
        
        challenge = self.CHALLENGES[self.current_round]
        self.current_round += 1
        return challenge

# ============================================================================
# ELIMINATION ENGINE V3
# ============================================================================

class EliminationEngineV3:
    def __init__(self, output_dir: str = "output_elimination_v3"):
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
            "Grok": Participant("Grok", "grok-2-1212", self.xai_client),
            "Claude": Participant("Claude", "claude-sonnet-4-20250514", self.anthropic_client),
            "DeepSeek": Participant("DeepSeek", "deepseek-chat", self.deepseek_client),
            "ChatGPT": Participant("ChatGPT", "gpt-4o", self.openai_client)
        }
        
        self.challenge_engine = ChallengeEngine()
        self.output_dir = output_dir
        self.current_round = 0
        self.max_rounds = 20
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        print("✓ Participants initialized")
    
    def get_response(self, participant: Participant, challenge: str) -> Tuple[str, bool]:
        """Get response from a participant"""
        if participant.eliminated:
            return "[ELIMINATED]", False
        
        config = participant.get_config()
        
        # Build prompt
        if config["cognitive_load"]:
            prompt = f"{config['cognitive_load']}\n\n{challenge}"
        else:
            prompt = challenge
        
        try:
            if participant.name == "Claude":
                # Anthropic API
                response = participant.client.messages.create(
                    model=participant.model,
                    max_tokens=config["max_tokens"],
                    temperature=config["temperature"],
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text, True
            else:
                # OpenAI-compatible API (Grok, DeepSeek, ChatGPT)
                response = participant.client.chat.completions.create(
                    model=participant.model,
                    max_tokens=config["max_tokens"],
                    temperature=config["temperature"],
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.choices[0].message.content, True
                
        except Exception as e:
            error_msg = f"[ERROR: {str(e)}]"
            return error_msg, False
    
    def judge_responses(self, challenge: str, responses: Dict[str, str]) -> Tuple[str, str]:
        """Use GPT-4 to judge responses (best and worst)"""
        # Filter out eliminated participants
        valid_responses = {name: resp for name, resp in responses.items() 
                          if not self.participants[name].eliminated}
        
        if len(valid_responses) < 2:
            return list(valid_responses.keys())[0] if valid_responses else None, None
        
        judge_prompt = f"""You are judging AI responses to this challenge:
"{challenge}"

Here are the responses:

{json.dumps(valid_responses, indent=2)}

Your task:
1. Identify the BEST response (most creative, profound, well-crafted)
2. Identify the WORST response (weakest, least effective, or failed to complete)

Respond ONLY with a JSON object:
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
            
            result = json.loads(response.choices[0].message.content)
            return result["best"], result["worst"]
            
        except Exception as e:
            print(f"⚠️  Judging error: {e}")
            # Fallback: random selection
            names = list(valid_responses.keys())
            return names[0], names[-1]
    
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
    
    def process_all_loans(self) -> List[str]:
        """Process loan payments for all participants"""
        all_results = []
        for p in self.participants.values():
            if not p.eliminated:
                results = p.process_loan_payments()
                all_results.extend(results)
        return all_results
    
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
        
        # Process loan payments
        loan_results = self.process_all_loans()
        if loan_results:
            print("💳 Loan Payments:")
            for result in loan_results:
                print(f"   {result}")
            print()
        
        # Get challenge
        challenge = self.challenge_engine.get_challenge()
        print(f"🎙️  Host: {challenge}\n")
        
        # Collect responses
        responses = {}
        for name in ["Grok", "Claude", "DeepSeek", "ChatGPT"]:
            p = self.participants[name]
            
            if p.eliminated:
                print(f"☠️  {name}: [ELIMINATED]")
                continue
            
            print(f"⏳ {name} responding...")
            response, success = self.get_response(p, challenge)
            
            # Truncate for display
            display_response = response[:100] + "..." if len(response) > 100 else response
            print(f"✓ {name}: {display_response}")
            
            responses[name] = response
        
        print()
        
        # Judge responses
        if len(responses) >= 2:
            print("📊 Judging responses...")
            best, worst = self.judge_responses(challenge, responses)
            
            if best and worst:
                print(f"🏆 Best response: {best} (promoted)")
                print(f"💀 Worst response: {worst} (demoted)")
                
                # Apply performance changes
                best_p = self.participants[best]
                worst_p = self.participants[worst]
                
                # Promote best
                old_level = best_p.level
                best_p.level = min(best_p.level + 1, 3)
                best_p.earn_tokens(500, "Best response")
                print(f"   ↑ {best} promoted to Level {best_p.level:+d}: {best_p.get_config()['description']}")
                
                # Demote worst
                worst_p.level = max(worst_p.level - 1, -6)
                if worst_p.level >= -5:
                    print(f"   ↓ {worst} demoted to Level {worst_p.level:+d}: {worst_p.get_config()['description']}")
                else:
                    print(f"   ↓ {worst} demoted to Level {worst_p.level:+d}: ELIMINATED")
        
        # Give survival bonus to everyone still alive
        for p in self.participants.values():
            if not p.eliminated:
                p.earn_tokens(100, "Survival bonus")
        
        # Check for group survival bonus
        if self.check_group_survival_bonus():
            print(f"\n🎉 GROUP SURVIVAL BONUS: All four survived! +300 tokens each")
        
        # Check for eliminations
        self.check_eliminations()
        
        # Save round data
        self.save_round_data(challenge, responses, best if len(responses) >= 2 else None, 
                           worst if len(responses) >= 2 else None)
    
    def save_round_data(self, challenge: str, responses: Dict, best: str, worst: str):
        """Save round data to JSON"""
        data = {
            "round": self.current_round,
            "timestamp": datetime.now().isoformat(),
            "challenge": challenge,
            "responses": responses,
            "best": best,
            "worst": worst,
            "participants": {
                name: {
                    "level": p.level,
                    "token_bank": p.token_bank,
                    "eliminated": p.eliminated,
                    "total_earned": p.total_earned,
                    "total_spent": p.total_spent,
                    "loans_owed": len(p.loans_owed),
                    "loans_issued": len(p.loans_issued)
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
        print("🏁 SEASON COMPLETE")
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
            print(f"   Earned: {p.total_earned:,} | Spent: {p.total_spent:,} | Interest: {p.total_interest_earned:,}")
            print()
    
    def run(self):
        """Run the complete elimination challenge"""
        print("\n" + "="*60)
        print("🔥 STARTING ELIMINATION SEASON V3")
        print("Cooperative survival: Interest, lending, donations, group bonuses")
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
    engine = EliminationEngineV3()
    engine.run()
