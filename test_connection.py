import logging
import json
from hyperliquid.info import Info
from hyperliquid.utils import constants

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_connection():
    logger.info("Starting Hyperliquid Connection Test...")
    
    try:
        # 1. Connect to Testnet Info API
        logger.info("Connecting to Hyperliquid Testnet Info API...")
        info = Info(constants.TESTNET_API_URL, skip_ws=True)
        
        # 2. Fetch User State (using a random address if none provided, or just check meta)
        # For this test, we just want to see if we can get market data (meta)
        logger.info("Fetching Exchange Metadata (Universe)...")
        meta = info.meta()
        
        universe = meta['universe']
        logger.info(f"Successfully fetched metadata. Total assets in universe: {len(universe)}")
        
        # 3. Fetch a specific price (e.g., ETH)
        target_coin = "ETH"
        logger.info(f"Fetching current price context for {target_coin}...")
        all_mids = info.all_mids()
        
        if target_coin in all_mids:
            price = all_mids[target_coin]
            logger.info(f"✅ SUCCESS: Current {target_coin} Price on Testnet: ${price}")
        else:
            logger.warning(f"⚠️  Could not find {target_coin} in market data.")
            
        return True

    except Exception as e:
        logger.error(f"❌ CONNECTION FAILED: {str(e)}")
        return False

if __name__ == "__main__":
    test_connection()
