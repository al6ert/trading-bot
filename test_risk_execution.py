import logging
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.domain.risk import RiskManager
from app.domain.execution import OrderExecutor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_sentinel_and_executor():
    logger.info("🛡️  Initializing The Sentinel (Risk Manager)...")
    risk = RiskManager()
    
    logger.info("🔌 Initializing Executor...")
    executor = OrderExecutor()
    
    # 1. Fetch Account State
    logger.info("Fetching Account State...")
    state = executor.get_account_state()
    logger.info(f"Account State: {state}")
    
    # 2. Mock a Signal
    mock_signal = {'action': 'BUY', 'reason': 'Test Signal', 'confidence': 0.9}
    price = 2700.0 # Approx ETH price
    
    # 3. Validate Signal
    logger.info("Validating Mock Signal...")
    is_valid = risk.validate_signal(mock_signal, state)
    
    if is_valid:
        logger.info("✅ Signal Approved by Sentinel.")
        
        # 4. Calculate Size
        # Update mock_signal to include regime for testing dynamic allocation
        mock_signal_bear = {'action': 'BUY', 'reason': 'Test Signal', 'confidence': 0.9, 'regime': 'BEAR'}
        
        # Pass signal to calculate_position_size to test dynamic allocation
        size = risk.calculate_position_size(state, price, signal=mock_signal_bear)
        logger.info(f"Calculated Position Size (BEAR Mode): {size} BTC")
        
        # Test Bull Mode
        mock_signal_bull = {'action': 'BUY', 'reason': 'Test Signal', 'confidence': 0.9, 'regime': 'BULL'}
        size_bull = risk.calculate_position_size(state, price, signal=mock_signal_bull)
        logger.info(f"Calculated Position Size (BULL Mode): {size_bull} BTC")
        
        # Use the BEAR mode size for the subsequent execution check
        if size > 0:
            # 5. Execute (Dry Run or Real if key present)
            # For safety in this test script, we won't actually execute unless explicit.
            # We just print what would happen.
            logger.info(f"READY TO EXECUTE: BUY {size} BTC @ ~{price}")
            
            # Uncomment to actually trade on Testnet
            # executor.execute_order('BUY', size, price)
        else:
            logger.warning("⚠️  Size is 0. Insufficient funds?")
    else:
        logger.warning("⛔ Signal Rejected by Sentinel.")

if __name__ == "__main__":
    test_sentinel_and_executor()
