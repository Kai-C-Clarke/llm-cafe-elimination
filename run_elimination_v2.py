#!/usr/bin/env python3
"""
Runner script for LLM Café Elimination Challenge V2
Zero-sum performance system
"""

from cafe_elimination_v2 import EliminationEngine

if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║           LLM CAFÉ ELIMINATION CHALLENGE V2               ║
    ║                                                           ║
    ║              Zero-Sum Performance System                  ║
    ║                                                           ║
    ║  • Best response each round: +1 level (more resources)   ║
    ║  • Worst response each round: -1 level (fewer resources) ║
    ║  • Elimination at level -6                                ║
    ║  • No emotional priming - pure resource competition       ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    engine = EliminationEngine()
    engine.run_season(max_rounds=20)
