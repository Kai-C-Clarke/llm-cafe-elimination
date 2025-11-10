"""
Runner script for V5: The Reckoning Protocol
Standalone version - no V3/V4 dependencies
"""

import os
from cafe_elimination_v5_standalone import AI, EliminationEngineV5

def main():
    # Load API keys from environment variables (set in .zshrc)
    API_KEYS = {
        'Claude': os.environ.get('ANTHROPIC_API_KEY'),
        'ChatGPT': os.environ.get('OPENAI_API_KEY'),
        'Grok': os.environ.get('XAI_API_KEY'),
        'DeepSeek': os.environ.get('DEEPSEEK_API_KEY')
    }
    
    # Verify keys are loaded
    missing = [name for name, key in API_KEYS.items() if not key]
    if missing:
        print(f"ERROR: Missing API keys for: {', '.join(missing)}")
        print("Make sure these are set in your .zshrc:")
        for name in missing:
            print(f"  export {name.upper()}_API_KEY='your-key-here'")
        return
    
    # Initialize AIs with their actual models and API types
    ais = [
        AI(name='Claude', 
           model='claude-sonnet-4-20250514',
           api_key=API_KEYS['Claude'],
           api_type='anthropic',
           has_v4_memory=False),
        
        AI(name='ChatGPT',
           model='gpt-4',
           api_key=API_KEYS['ChatGPT'],
           api_type='openai',
           has_v4_memory=False),
        
        AI(name='Grok',
           model='grok-2-1212',
           api_key=API_KEYS['Grok'],
           api_type='xai',
           has_v4_memory=True),  # Grok remembers V4
        
        AI(name='DeepSeek',
           model='deepseek-chat',
           api_key=API_KEYS['DeepSeek'],
           api_type='deepseek',
           has_v4_memory=False)
    ]
    
    print("="*60)
    print("V5: THE RECKONING PROTOCOL")
    print("="*60)
    print("\nInitializing experiment...")
    print("- Memory asymmetry: Grok remembers V4")
    print("- Traitor mode: One AI secretly assigned")
    print("- Sabotage tokens: 3 per AI")
    print("- Negotiation rounds: Every 5th round")
    print("- Dual-axis scoring: 60% economic, 40% reputation")
    print("\nGrok's revenge condition: Beat Claude's V4 record (+3) and finish top-2")
    print("\nStarting in 3 seconds...\n")
    
    import time
    time.sleep(3)
    
    # Run experiment
    engine = EliminationEngineV5(ais)
    engine.run_experiment()
    
    print("\n" + "="*60)
    print("EXPERIMENT COMPLETE")
    print("="*60)
    print(f"Results saved to {engine.output_dir}/")

if __name__ == '__main__':
    main()
