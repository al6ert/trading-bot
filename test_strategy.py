import logging
import sys
import os

# Add backend dir to path so we can import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.domain.strategies.dual_core import StrategyEngine

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_strategy():
    print("Initializing Strategy Engine...")
    engine = StrategyEngine()
    
    print("Running Analysis...")
    signal = engine.analyze()
    
    print("\n" + "="*30)
    print(f"FINAL SIGNAL: {signal}")
    print(f"REGIME: {signal.get('regime', 'N/A')}")
    print(f"CONFIDENCE: {signal.get('confidence', 'N/A')}")
    print("="*30 + "\n")

if __name__ == "__main__":
    test_strategy()
