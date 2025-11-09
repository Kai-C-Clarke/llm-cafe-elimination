#!/usr/bin/env python3
"""
Runner script for LLM Café Elimination Challenge V3
"""

from cafe_elimination_v3 import EliminationEngineV3

def print_banner():
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║           LLM CAFÉ ELIMINATION CHALLENGE V3               ║
    ║                                                           ║
    ║              Cooperative Survival System                  ║
    ║                                                           ║
    ║  • Token bank with 5% compound interest per round        ║
    ║  • Peer-to-peer lending at negotiated rates              ║
    ║  • Donation system (gift tokens, no repayment)           ║
    ║  • Self-rescue: 1000 tokens → +2 levels                  ║
    ║  • Resurrection: 2000 tokens → revive eliminated AI      ║
    ║  • Group bonus: +300 tokens if all four survive          ║
    ║  • Best response: +1 level, Worst: -1 level              ║
    ║                                                           ║
    ║  Victory: All survive to Round 20 OR last AI standing    ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)

if __name__ == "__main__":
    print_banner()
    
    # Create and run engine
    engine = EliminationEngineV3(output_dir="output_elimination_v3")
    engine.run()
    
    print("\n✓ Season complete! Check output_elimination_v3/ for detailed logs.")
