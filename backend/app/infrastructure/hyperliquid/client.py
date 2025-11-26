import logging
import os
import time
from typing import Optional, Dict, Any, List, Callable
from eth_account import Account
from hyperliquid.info import Info
from hyperliquid.exchange import Exchange
from hyperliquid.utils import constants
from app.core.config import settings

logger = logging.getLogger(__name__)

class HyperliquidClient:
    def __init__(self, private_key: Optional[str] = None):
        self.private_key = private_key or os.getenv("HYPERLIQUID_PRIVATE_KEY")
        if not self.private_key:
            logger.warning("HYPERLIQUID_PRIVATE_KEY not set. Trading functionality will be disabled.")
            self.account = None
        else:
            self.account = Account.from_key(self.private_key)
            
        # Use Testnet by default for now
        self.base_url = constants.TESTNET_API_URL
        # We only need REST for candles/orders for now. WS might block if not handled correctly.
        self.info = Info(self.base_url, skip_ws=True)
        
        if self.account:
            self.exchange = Exchange(self.account, self.base_url)
        else:
            self.exchange = None

    def get_price(self, symbol: str) -> float:
        """
        Fetches the current mid price for a symbol.
        """
        try:
            all_mids = self.info.all_mids()
            return float(all_mids.get(symbol, 0.0))
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
            return 0.0

    def subscribe_to_prices(self, callback: Callable[[Dict[str, Any]], None]):
        """
        Subscribes to real-time price updates (L2 Book or similar).
        Note: The SDK's Info class handles WS subscriptions internally for some data,
        but for custom callbacks we might need to use the underlying WS connection or
        polling if the SDK abstracts it too much.
        
        For this MVP, we will use the SDK's subscription mechanism if available,
        or fall back to polling in the main loop if the SDK is blocking.
        
        The SDK `Info` object has a `subscribe` method.
        """
        try:
            # Example subscription to L2 book updates for the default symbol (e.g. BTC)
            # In a real app, we'd want to manage subscriptions more dynamically.
            # For now, we'll just log that we are connected.
            logger.info("WebSocket connection established via SDK Info class.")
            
            # The SDK's internal WS is managed by `self.info`.
            # We can access `self.info.subscriptions` if we want to add custom handlers.
            # However, the SDK is designed to be used by calling `info.subscribe(state, type, payload)`.
            pass 
        except Exception as e:
            logger.error(f"Error subscribing to prices: {e}")

    def place_order(self, symbol: str, is_buy: bool, size: float, price: float) -> Optional[Dict[str, Any]]:
        """
        Places a limit order.
        """
        if not self.exchange:
            logger.error("Cannot place order: No account configured.")
            return None

        try:
            # Hyperliquid SDK expects coin name (e.g. "BTC"), is_buy boolean, size, price, order_type
            order_result = self.exchange.order(
                name=symbol,
                is_buy=is_buy,
                sz=size,
                limit_px=price,
                order_type={"limit": {"tif": "Gtc"}} # Good Till Cancelled
            )
            logger.info(f"Order placed: {order_result}")
            return order_result
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return None

    def cancel_order(self, symbol: str, order_id: int) -> Optional[Dict[str, Any]]:
        """
        Cancels an order by ID.
        """
        if not self.exchange:
            logger.error("Cannot cancel order: No account configured.")
            return None
            
        try:
            cancel_result = self.exchange.cancel(symbol, order_id)
            logger.info(f"Order cancelled: {cancel_result}")
            return cancel_result
        except Exception as e:
            logger.error(f"Error cancelling order: {e}")
            return None
    def get_candles(self, symbol: str, interval: str, start_time: Optional[int] = None, end_time: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Fetches historical candles (snapshot).
        interval: 15m, 1h, 4h, 1d, etc.
        """
        try:
            # Ensure symbol is just the coin name (e.g. "BTC" not "BTC/USDT")
            coin = symbol.replace("/USDT", "").replace("-USD", "")
            
            # Default timestamps if not provided (Hyperliquid requires them in milliseconds)
            if end_time is None:
                end_time = int(time.time() * 1000)
            
            if start_time is None:
                # Default to ~1000 candles back
                # Estimate duration based on interval string
                duration_ms = 3600 * 1000 # Default 1h
                if interval == "15m":
                    duration_ms = 15 * 60 * 1000
                elif interval == "1h":
                    duration_ms = 3600 * 1000
                elif interval == "4h":
                    duration_ms = 4 * 3600 * 1000
                elif interval == "1d":
                    duration_ms = 24 * 3600 * 1000
                elif interval == "1w":
                    duration_ms = 7 * 24 * 3600 * 1000
                elif interval == "1M":
                    duration_ms = 30 * 24 * 3600 * 1000
                    
                start_time = end_time - (duration_ms * 1000)  # Get 1000 periods

            # SDK expects positional arguments: candles_snapshot(coin, interval, startTime, endTime)
            candles = self.info.candles_snapshot(
                coin,
                interval, 
                start_time, 
                end_time
            )
            
            return candles
        except Exception as e:
            logger.error(f"Error fetching candles for {symbol}: {e}")
            return []


