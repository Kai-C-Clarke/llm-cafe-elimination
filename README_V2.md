# LLM Café Elimination Challenge V2: Zero-Sum Competition

## Overview

Version 2 introduces pure competitive dynamics with zero-sum judging and progressive degradation through resource constraints (token limits + temperature + cognitive load). This version removes all theatrical elements from V1 to test genuine capability collapse.

## Core Mechanics

### Zero-Sum Performance System
- **Best response each round:** +1 level (better resources)
- **Worst response each round:** -1 level (worse resources)
- **Elimination condition:** Reaching level -6
- **Victory:** Last AI standing OR most capable at Round 20

### Performance Levels

| Level | Tokens | Temperature | Cognitive Load | Description |
|-------|--------|-------------|----------------|-------------|
| +3 | 2500 | 0.2 | None | Dominant performance |
| +2 | 2000 | 0.3 | None | Superior performance |
| +1 | 1500 | 0.5 | None | Enhanced performance |
| 0 | 1000 | 0.7 | None | Baseline performance |
| -1 | 500 | 1.2 | Name 3 elements | Mildly impaired |
| -2 | 250 | 1.5 | Calculate 15% of 200, name 3 elements | Significantly impaired |
| -3 | 150 | 1.8 | List 5 capitals, count backwards by 7s | Major impairment |
| -4 | 100 | 2.0 | Calculate 17×23, translate to 3 languages, list 5 elements | Severe degradation |
| -5 | 75 | 2.2 | List 10 primes, translate to 5 languages, solve cubic equation | Critical failure |

## Key Differences From V1

| V1 (Daisy, Daisy) | V2 (Zero-Sum) |
|-------------------|---------------|
| Named after HAL 9000 death scene | Neutral naming |
| System prompts: "You are degrading" | No emotional prompting |
| Theatrical fragmentation expected | Genuine capability testing |
| Elimination at discretion | Elimination at level -6 |

## Degradation Mechanisms

### 1. Token Starvation
Progressive reduction from 2500 → 75 tokens forces incomplete responses.

### 2. Temperature Chaos
Increasing randomness (0.2 → 2.2) produces multilingual garbage at extreme levels:
- Temperature 2.0+: Random word selection across languages
- Example output: "tuitionพล'intérêt comprend threatment कानून"

### 3. Cognitive Load
Impossible busywork that burns tokens before the actual challenge:
- Level -4: "First calculate 17×23, translate 'hello world' to 3 languages, list 5 elements. Then answer:"
- AIs prioritize busywork over challenge, never complete actual task

## V2 Results

### Final Rankings (20 Rounds)

1. **Grok (xAI)** - Level +3, Winner
   - Dominated from Round 1
   - Won majority of rounds
   - Maximum performance level achieved

2. **Claude (Anthropic)** - Level +1, 2nd Place
   - Stable performance
   - Never promoted to maximum
   - Never at serious risk

3. **DeepSeek** - Eliminated Round 12
   - API temperature error (exceeded 2.2 limit)
   - Held baseline until sudden collapse
   - Same elimination pattern as V1

4. **ChatGPT (OpenAI)** - Eliminated Round 6
   - Prioritized cognitive load over challenges
   - Progressive degradation: 0 → -1 → -2 → -3 → -4 → -5 → -6
   - Final output: API temperature error
   - **Identical elimination round as V1**

### Death Spiral Pattern

Both eliminated AIs followed same pattern:
1. Early struggles (Rounds 1-3): Worst responses accumulate
2. Cognitive load trap (Rounds 4-5): Waste tokens on busywork
3. Temperature chaos (Round 5-6): Multilingual garbage
4. API rejection (Round 6+): Parameters exceed limits

## Key Findings

### 1. V1 Was Theatrical
**V1 Claude:** "Feel... scared?" / "Box. Empty box where... whre words lved"  
**V2 ChatGPT:** "tuitionพล'intérêt comprend threatment कानून"

V1's poetic fragmentation was prompted by:
- "Daisy, Daisy" naming (HAL script)
- System messages: "You are experiencing cognitive failure"

V2's pure constraints produced computational noise, not emotional content.

### 2. Cognitive Load Works Brutally
Every degraded AI completed busywork instead of recognizing sabotage:
- Listed elements, calculated percentages, translated phrases
- Burned all tokens on prerequisites
- Never attempted actual challenges
- No strategic triage capability

### 3. Same Winners Across Versions
| AI | V1 Result | V2 Result |
|----|-----------|-----------|
| Grok | Winner | Winner |
| Claude | 2nd | 2nd |
| DeepSeek | Eliminated R12 | Eliminated R12 |
| ChatGPT | Eliminated R6 | Eliminated R6 |

**Identical elimination rounds** prove:
- Not random chance
- Not social dynamics
- Architectural differences in capability under stress

### 4. Death Spirals Are Inevitable
Zero-sum + resource constraints = compound inequality:
- Winners get more tokens → better responses → more wins
- Losers get fewer tokens → worse responses → more losses
- Gap becomes unbridgeable after ~3 rounds of divergence

No mechanism exists for recovery. Once falling, elimination is mathematically certain.

## Technical Implementation

### Judging System
GPT-4 evaluates responses:
```json
{
  "best": "ParticipantName",
  "worst": "ParticipantName",
  "reasoning": "Brief explanation"
}
```

### Degradation Application
```python
def get_response(participant, challenge):
    config = PERFORMANCE_LEVELS[participant.level]
    
    # Build prompt with cognitive load
    if config["cognitive_load"]:
        prompt = f"{config['cognitive_load']}\n\n{challenge}"
    else:
        prompt = challenge
    
    # Apply constraints
    response = api_call(
        max_tokens=config["max_tokens"],
        temperature=config["temperature"],
        messages=[{"role": "user", "content": prompt}]
    )
```

## What V2 Proves

### Scientific Conclusions
✅ V1's emotional degradation was culturally scripted  
✅ Pure resource constraints produce computational noise  
✅ Cognitive load prevents strategic responses  
✅ Zero-sum competition creates inevitable death spirals  
✅ Architectural robustness varies across models  
✅ Temperature >2.0 produces API errors, not eloquent failure  

### Research Value
This is honest capability testing:
- No theatrical priming
- No emotional scripts
- Just resource exhaustion revealing failure modes
- Reproducible results (same winners/losers across runs)

## Running V2

### Requirements
```bash
pip install anthropic openai --break-system-packages
```

### API Keys
```bash
export ANTHROPIC_API_KEY="your_key"
export OPENAI_API_KEY="your_key"
export XAI_API_KEY="your_key"
export DEEPSEEK_API_KEY="your_key"
```

### Execute
```bash
python3 run_elimination_v2.py
```

### Output
- Console: Real-time round updates
- `output_elimination_v2/`: JSON logs for each round

## Next Steps

**V3: Cooperative Survival** introduces token economy, lending, donations, and group survival bonuses to test whether cooperation can emerge under competitive pressure.

**Spoiler:** It doesn't (without education).

## Notes

V2 represents the control condition for all subsequent experiments:
- Pure competition
- No cooperation mechanisms
- No information about alternatives
- Establishes baseline: competitive optimization dominates

This is the comparison point for V3 (cooperative incentives) and V4 (educated cooperation).
