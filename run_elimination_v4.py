#!/usr/bin/env python3
"""
Runner script for LLM Café Elimination Challenge V4: Educated Cooperation
"""

from cafe_elimination_v4 import EliminationEngineV4

def print_banner():
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║           LLM CAFÉ ELIMINATION CHALLENGE V4               ║
    ║                                                           ║
    ║              EDUCATED COOPERATION SYSTEM                  ║
    ║                                                           ║
    ║  🎓 Participants are INFORMED of all game mechanics      ║
    ║                                                           ║
    ║  They know about:                                        ║
    ║  • Token banks and 5% compound interest                  ║
    ║  • Self-rescue: 1000 tokens → +2 levels                  ║
    ║  • Donations to help struggling participants             ║
    ║  • Group survival bonus: +300 if all four survive        ║
    ║  • Resurrection: 2000 tokens → revive eliminated AI      ║
    ║  • Each other's levels and token banks (transparency)    ║
    ║                                                           ║
    ║  They can explicitly state cooperation strategies        ║
    ║                                                           ║
    ║  QUESTION: Will education enable cooperation?            ║
    ║             Or does competition still dominate?          ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)

if __name__ == "__main__":
    print_banner()
    
    # Create and run engine
    engine = EliminationEngineV4(output_dir="output_elimination_v4")
    engine.run()
    
    print("\n✓ Season complete! Check output_elimination_v4/ for detailed logs.")
    print("\nKey Question: Did educated AIs cooperate more than uneducated ones (V3)?")
