import logging
import os
from hyperliquid.exchange import Exchange
from hyperliquid.utils import constants
from eth_account.signers.local import LocalAccount
from eth_account import Account
from app.core.config import settings

logger = logging.getLogger(__name__)

class OrderExecutor:
    def __init__(self):
        self.env = constants.TESTNET_API_URL if settings.HYPERLIQUID_ENV == "TESTNET" else constants.MAINNET_API_URL
        self.private_key = settings.PRIVATE_KEY
        self.account: LocalAccount = None
        self.exchange: Exchange = None
        
        if self.private_key:
            try:
                self.account = Account.from_key(self.private_key)
                # Initialize Exchange with the account
                # Note: In a real "API Agent" flow, we might use a different address for the agent
                # than the main wallet, but the signing logic is the same.
                self.exchange = Exchange(self.account, self.env)
                logger.info(f"🔌 Executor initialized for address: {self.account.address}")
            except Exception as e:
                logger.error(f"Failed to initialize Executor: {e}")

    def get_account_state(self) -> dict:
        """
        Fetches current balance and equity.
        """
        if not self.exchange:
            return {'total_equity': 0.0, 'available_balance': 0.0, 'positions': []}
            
        try:
            user_state = self.exchange.info.user_state(self.account.address)
            margin_summary = user_state.get('marginSummary', {})
            
            total_equity = float(margin_summary.get('accountValue', 0.0))
            # In Hyperliquid, 'withdrawable' is a good proxy for available USDC for spot?
            # Or 'totalMargin' if using cross. 
            # For Spot, we look at the Spot balances usually.
            # Let's assume we are trading Perps for now as Hyperliquid is Perp-first, 
            # BUT the user said "Spot Only". 
            # Hyperliquid Spot API is slightly different. 
            # The SDK supports spot. We need to check spot balances.
            
            # Checking spot state
            spot_state = self.exchange.info.spot_user_state(self.account.address)
            balances = spot_state.get('balances', [])
            
            usdc_balance = 0.0
            for bal in balances:
                if bal['coin'] == 'USDC':
                    usdc_balance = float(bal['total']) # 'total' or 'hold'?
                    break
            
            # If Spot State is empty (no interaction yet), fallback to 0
            
            return {
                'total_equity': usdc_balance, # Simplified for Spot-only portfolio
                'available_balance': usdc_balance,
                'positions': balances
            }
            
        except Exception as e:
            logger.error(f"Error fetching account state: {e}")
            return {'total_equity': 0.0, 'available_balance': 0.0, 'positions': []}

    def execute_order(self, action: str, size: float, price: float = None):
        """
        Executes a MARKET order (for MVP simplicity).
        """
        if not self.exchange:
            logger.error("Cannot execute: No Exchange connection.")
            return

        is_buy = action == 'BUY'
        
        logger.info(f"🚀 EXECUTING {action} | Size: {size} | Symbol: {settings.SYMBOL}")
        
        try:
            # Hyperliquid Spot Order
            # coin: str (e.g. "ETH")
            # is_buy: bool
            # sz: float
            # limit_px: float (For market orders, use aggressive limit or specific market method)
            # order_type: dict (e.g. {"limit": {"tif": "Gtc"}})
            
            # For Market Order in Spot:
            # We usually send a Limit order crossing the book (IoC or aggressive price).
            # Or use the 'market_open' helper if available.
            
            # Let's try a Market Order via SDK helper if possible, or aggressive limit.
            # SDK 'market_open' is for perps. Spot might need 'order' method.
            
            # Constructing the order
            # Price: If Buy, Price = Current * 1.05 (Slippage tolerance)
            # Price: If Sell, Price = Current * 0.95
            
            exec_price = price * 1.05 if is_buy else price * 0.95
            
            # Rounding price to tick size (assuming 0.1 for BTC for now, need meta)
            exec_price = round(exec_price, 1)
            
            result = self.exchange.order(
                name=settings.SYMBOL,
                is_buy=is_buy,
                sz=size,
                limit_px=exec_price,
                order_type={"limit": {"tif": "Ioc"}}, # Immediate or Cancel for "Market-like"
                vault_address=None # Spot usually doesn't use vault address like perps?
            )
            
            status = result['status']
            if status == 'ok':
                logger.info(f"✅ ORDER FILLED: {result}")
            else:
                logger.error(f"❌ ORDER FAILED: {result}")
                
        except Exception as e:
            logger.error(f"Execution Exception: {e}")
