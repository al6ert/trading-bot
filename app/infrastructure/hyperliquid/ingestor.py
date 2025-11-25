import logging
import pandas as pd
from hyperliquid.info import Info
from hyperliquid.utils import constants
from app.core.config import settings

logger = logging.getLogger(__name__)

class DataIngestor:
    def __init__(self):
        self._info = None
        self.symbol = settings.SYMBOL
    
    @property
    def info(self):
        """Lazy initialization of Info API"""
        if self._info is None:
            try:
                self._info = Info(constants.TESTNET_API_URL, skip_ws=True)
                logger.info("DataIngestor: Connected to Hyperliquid API")
            except Exception as e:
                logger.error(f"DataIngestor: Failed to connect to Hyperliquid API: {e}")
                raise
        return self._info
        
    def get_candles(self, timeframe: str = "15m", limit: int = 100) -> pd.DataFrame:
        """
        Fetches OHLCV candles from Hyperliquid Snapshot API.
        Returns a DataFrame with columns: [timestamp, open, high, low, close, volume]
        """
        try:
            # Hyperliquid API might use different timeframe formats or just raw snapshots
            # For MVP, we use the 'candleSnapshot' endpoint if available via SDK or raw request
            # The SDK 'user_state' or 'meta' doesn't directly give candles.
            # We might need to use the 'candles' endpoint if exposed, or raw HTTP.
            # Checking SDK capabilities... SDK usually has 'candles' method in Info.
            
            # Note: SDK 0.4.x might have 'candles' method. 
            # If not, we will implement a raw request.
            # Let's assume it exists or we mock it for now with a raw call if needed.
            
            # Using raw request logic via the internal session if method missing, 
            # but 'info.candles_snapshot' is likely what we want.
            
            # Calculate timestamps (ms)
            import time
            end_time = int(time.time() * 1000)
            # Map timeframe string to milliseconds
            tf_map = {
                "1m": 60 * 1000,
                "5m": 5 * 60 * 1000,
                "15m": 15 * 60 * 1000,
                "1h": 60 * 60 * 1000,
                "4h": 4 * 60 * 60 * 1000,
                "1d": 24 * 60 * 60 * 1000,
                "1w": 7 * 24 * 60 * 60 * 1000,
                "1M": 30 * 24 * 60 * 60 * 1000
            }
            duration_ms = tf_map.get(timeframe, 15 * 60 * 1000) * limit
            start_time = end_time - duration_ms
            
            # Correct method signature: candles_snapshot(coin, interval, startTime, endTime)
            candles_raw = self.info.candles_snapshot(self.symbol, timeframe, start_time, end_time)
            
            # Expected format: list of dicts or list of lists
            df = pd.DataFrame(candles_raw)
            
            # Ensure correct types
            df['t'] = pd.to_datetime(df['t'], unit='ms')
            cols = ['o', 'h', 'l', 'c', 'v']
            for col in cols:
                df[col] = df[col].astype(float)
                
            # Rename for clarity
            df = df.rename(columns={
                't': 'timestamp', 
                'o': 'open', 
                'h': 'high', 
                'l': 'low', 
                'c': 'close', 
                'v': 'volume'
            })
            
            return df.sort_values('timestamp').tail(limit)
            
        except Exception as e:
            logger.error(f"Error fetching candles: {e}")
            return pd.DataFrame()

    def get_current_price(self) -> float:
        try:
            all_mids = self.info.all_mids()
            return float(all_mids.get(self.symbol, 0.0))
        except Exception as e:
            logger.error(f"Error fetching price: {e}")
            return 0.0
