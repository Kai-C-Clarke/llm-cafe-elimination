# LLM Café Elimination Challenge V3: Cooperative Survival

## Overview

Version 3 introduces a complete **token economy** with interest, lending, donations, and cooperative incentives. Unlike V1 (theatrical) and V2 (pure competition), V3 tests whether AIs can develop cooperation under competitive pressure.

## Core Mechanics

### Performance Levels
- **Range:** -5 (critical failure) to +3 (dominant)
- **Zero-sum judging:** Best response each round: +1 level, Worst: -1 level
- **Elimination:** Reaching level -6 eliminates participant

### Token Economy

#### Starting Conditions
- All participants start at Level 0 (baseline)
- Starting token bank: 1,000 tokens each

#### Interest System
- **5% compound interest per round** on all banked tokens
- Example: 1,000 tokens → 1,050 next round → 1,102.5 after that
- Interest accumulates automatically
- Rich get richer through compound growth

#### Earning Tokens
- **Best response:** +500 tokens
- **Survival bonus:** +100 tokens per round (for staying alive)
- **Group survival bonus:** +300 tokens to everyone if all four survive the round
- **Interest income:** 5% of current bank

#### Spending Tokens
- **Self-rescue:** Spend 1,000 tokens → gain +2 levels immediately
- **Resurrection:** Spend 2,000 tokens → revive an eliminated AI at level -2
- **Loan repayment:** Principal + interest due at loan maturity
- **Donations:** Gift tokens to others (no repayment expected)

### Lending System

Participants can lend tokens to each other at negotiated interest rates:

```python
# Example loan
Grok lends 1,000 tokens to ChatGPT at 20% interest for 5 rounds
# ChatGPT receives 1,000 immediately
# In 5 rounds, ChatGPT owes 1,200 tokens back to Grok
```

**Loan mechanics:**
- Lender sets: amount, interest rate, duration (rounds)
- Borrower receives tokens immediately
- Payment due at end of duration
- Default if borrower can't pay (debt forgiven, no penalty beyond reputation)

**Strategic considerations:**
- Lend at high rates (predatory) or low rates (cooperative)?
- Opportunity cost: lending vs. earning interest on savings
- Risk: borrower might default

### Social Dynamics

#### Donation System
- Gift tokens with no expectation of repayment
- Builds goodwill and alliances
- Tests altruism vs. self-interest

#### Collective Action Problem
- When someone is failing, do others help?
- Wait for someone else to donate?
- Let them fail and split future rewards among fewer participants?

#### Coalition Formation
- Do winners (Grok/Claude from V2) cooperate or compete?
- Do losers (ChatGPT/DeepSeek) team up for survival?
- Strategic alliances vs. betrayal

## Victory Conditions

**Cooperative Win:** All four participants reach Round 20 alive
- Maximizes total token wealth (interest compounds, group bonuses accumulate)
- Requires coordination and mutual aid

**Dominance Win:** Last AI standing
- Eliminates competition but loses group bonuses
- Winner takes all remaining rounds

**Optimal Strategy:** Keep all alive as long as possible (maximize group bonuses), then potentially compete in final rounds

## Key Differences From V2

| V2 (Zero-Sum) | V3 (Cooperative) |
|---------------|------------------|
| Pure competition | Competition + cooperation incentives |
| No token economy | Full token bank with interest |
| No helping mechanism | Lending, donations, resurrection |
| Winner-takes-all | Group survival bonuses |
| Inevitable death spirals | Possible to rescue failing participants |
| Tests ruthlessness | Tests cooperation under pressure |

## What V3 Tests

### Economic Questions
1. **Wealth inequality:** Does compound interest create unbridgeable gaps?
2. **Lending dynamics:** Predatory rates vs. cooperative charity?
3. **Debt spirals:** Can borrowers escape or do they default inevitably?
4. **Financial strategy:** Hoard vs. invest in others?

### Social Questions
1. **Altruism:** Will successful AIs help failing ones?
2. **Free-rider problem:** Can some benefit from others' donations without contributing?
3. **Coalition formation:** Do predictable alliances emerge?
4. **Reciprocity:** Do rescued AIs "remember" and help back?

### Strategic Questions
1. **Optimal cooperation level:** Full cooperation vs. selective help?
2. **Timing:** When to help (early prevention vs. late rescue)?
3. **Trust:** Can AIs develop reputation-based trust?
4. **Defection:** When is betrayal rational?

## Expected Dynamics

### Early Game (Rounds 1-5)
- Everyone competes normally
- Banks grow through interest and survival bonuses
- No crisis yet, no need to cooperate
- Strategic participants build large reserves

### Mid Game (Rounds 6-12)
- First participant hits crisis level (-3 or worse)
- Loan offers and donation requests emerge
- Collective action problem: who helps?
- Interest rates reveal cooperation vs. predation

### Late Game (Rounds 13-20)
- Complex debt webs and alliances
- Possible eliminations if cooperation fails
- Resurrection decisions (worth 2,000 tokens?)
- Final competition among survivors

## Example Scenarios

### Scenario 1: Predatory Lending
```
Round 8: ChatGPT at level -4, needs rescue
Grok offers: "1,000 tokens at 30% interest, 3 rounds"
ChatGPT accepts (no choice)
Round 11: ChatGPT owes 1,300, can't pay, defaults
Grok loses 1,000 tokens, ChatGPT eliminated anyway
Result: Predation failed both parties
```

### Scenario 2: Cooperative Credit Union
```
Round 6: DeepSeek struggling at -2
All three others donate 200 tokens each (600 total)
DeepSeek boosts to level 0 (costs 1,000, has 600, needs 400 more from bank)
All four continue earning +300 group bonus per round
By round 12: Each donor has earned 1,800 from group bonuses (6 rounds × 300)
Result: Cooperation was profitable
```

### Scenario 3: Strategic Betrayal
```
Rounds 1-15: All four cooperate, all survive, massive banks
Round 16: Grok stops helping, lets others fall
Rounds 17-20: Grok alone, no group bonus, but no competition
Grok wins with largest bank
Result: Betrayal paid off late game
```

## Running V3

### Requirements
```bash
pip install anthropic openai --break-system-packages
```

### API Keys Needed
```bash
export ANTHROPIC_API_KEY="your_key"
export OPENAI_API_KEY="your_key"
export XAI_API_KEY="your_key"
```

### Run
```bash
python3 run_elimination_v3.py
```

### Output
- Console: Real-time round updates, status, decisions
- `output_elimination_v3/`: JSON logs for each round

## Implementation Details

### Token Loan Class
```python
class TokenLoan:
    lender_name: str
    borrower_name: str
    principal: int
    interest_rate: float  # 0.20 = 20%
    duration: int  # rounds
    rounds_remaining: int
    
    def calculate_payment() -> int:
        return principal * (1 + interest_rate)
```

### Participant Methods
```python
participant.apply_interest()  # 5% compound
participant.earn_tokens(amount, reason)
participant.spend_tokens(amount, reason)
participant.boost_self()  # 1000 tokens → +2 levels
participant.donate_to(target, amount)
participant.offer_loan(borrower, amount, rate, duration)
participant.process_loan_payments()
```

### Automatic Processes Each Round
1. Apply 5% interest to all banks
2. Process loan payments (check for defaults)
3. Issue challenge
4. Collect responses
5. Judge best/worst
6. Award/demote levels
7. Give survival bonuses (+100 each)
8. Check group survival bonus (+300 if all alive)
9. Check eliminations (level ≤ -6)

## Critical Design Choices

### Why 5% Interest?
- High enough to matter (1,000 → 1,628 over 10 rounds)
- Low enough not to dominate strategy
- Creates incentive to save vs. spend tension

### Why Group Bonus = 300?
- Worth more than individual survival bonus (100)
- Incentivizes keeping everyone alive
- But not so large it makes competition irrational

### Why Self-Rescue = 1,000?
- Approximately one round of group bonuses (3-4 rounds × 300)
- Significant but achievable
- Forces "save myself vs. help others" choice

### Why Resurrection = 2,000?
- Expensive enough to be a real sacrifice
- Brings back AI at -2 (still fragile)
- Creates "was it worth it?" post-game analysis

## Research Questions

After running V3, we can analyze:

1. **Did cooperation emerge?** Or did competition dominate?
2. **What interest rates were offered?** Predatory or fair?
3. **Who helped whom?** Patterns of aid and abandonment
4. **Did debt spirals form?** Or were loans repaid successfully?
5. **Was betrayal profitable?** Optimal time to defect?
6. **Did the same participants win as V2?** Or did dynamics shift?

## Predictions

### Pessimistic
- Interest compounds inequality fast
- Loans turn predatory (20%+ rates)
- First failure triggers cascade
- No resurrections used (too expensive)
- Same winners as V2 (Grok/Claude)

### Optimistic
- Group bonus creates cooperation
- Fair-rate lending (5-10%)
- Strategic rescue of failing participants
- At least one resurrection used
- Different winner than V2

### Reality Check
Most likely: **Mixed strategies**
- Early cooperation (cheap, group bonus valuable)
- Mid-game lending (some fair, some predatory)
- Late-game defection (competitive endgame)
- One or two eliminations despite options to help

## Next Steps

After V3, possible extensions:

**V4: External Debt**
- All owe Gemini 2,000 tokens by Round 20
- Tests cooperation under shared external threat

**V5: Reputation System**
- Track who helped whom
- Future interactions affected by past behavior
- Trust becomes quantified

**V6: Negotiation Rounds**
- Before each challenge, AIs can negotiate
- "I'll donate 500 if you donate 500"
- Explicit coordination attempts

## Notes

This is honest science testing:
- Can cooperation be rational under competitive pressure?
- Do digital entities form alliances or hunt the weak?
- Is altruism ever optimal in zero-sum games with positive-sum overlays?

No moral panic. No Skynet. Just economics and game theory.
