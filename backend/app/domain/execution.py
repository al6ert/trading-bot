import logging
import asyncio
from typing import List
from hyperliquid.info import Info
from hyperliquid.utils import constants
from app.core.config import settings
from app.domain.schemas import PortfolioState, Position, OrderRequest, OrderResult, TradeAction
from app.domain.interfaces import IExecutor
from datetime import datetime

logger = logging.getLogger(__name__)

class OrderExecutor(IExecutor):
    def __init__(self):
        self.env = constants.TESTNET_API_URL if settings.HYPERLIQUID_ENV == "TESTNET" else constants.MAINNET_API_URL
        self.public_address = settings.PUBLIC_ADDRESS
        
        if not self.public_address:
            logger.warning("⚠️ PUBLIC_ADDRESS not set. Portfolio state will be empty.")
        
        # Initialize Info API (Read-Only, No Private Key needed)
        self.info = Info(self.env, skip_ws=True)
        logger.info(f"🔌 Executor initialized in Non-Custodial Mode (Read-Only). Address: {self.public_address}")

    async def get_portfolio_state(self) -> PortfolioState:
        """
        Fetches current balance and equity asynchronously using public Info API.
        """
        if not self.public_address:
            return PortfolioState(total_equity=0.0, available_balance=0.0, positions=[])
            
        try:
            # Run blocking SDK call in a thread
            spot_state = await asyncio.to_thread(
                self.info.spot_user_state, 
                self.public_address
            )
            
            balances = spot_state.get('balances', [])
            
            usdc_balance = 0.0
            positions = []
            
            for bal in balances:
                coin = bal['coin']
                total = float(bal['total'])
                
                if coin == 'USDC':
                    usdc_balance = total
                else:
                    if total > 0:
                        positions.append(Position(
                            symbol=coin,
                            side="LONG",
                            size=total,
                            entry_price=0.0, # Placeholder, requires fills history for accuracy
                            unrealized_pnl=0.0
                        ))
            
            return PortfolioState(
                total_equity=usdc_balance, # Simplified
                available_balance=usdc_balance,
                positions=positions,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error fetching account state: {e}")
            return PortfolioState(total_equity=0.0, available_balance=0.0, positions=[])

    async def execute_order(self, order: OrderRequest) -> OrderResult:
        """
        Constructs the order payload for the Frontend to sign. 
        Does NOT execute the order directly (Non-Custodial).
        """
        is_buy = order.action == TradeAction.BUY
        
        logger.info(f"📝 PREPARING ORDER PAYLOAD {order.action} | Size: {order.size} | Symbol: {order.symbol}")
        
        try:
            # Price Logic
            if order.price is None:
                return OrderResult(order_id="", status="FAILED", error_message="Price required for execution")

            exec_price = order.price * 1.05 if is_buy else order.price * 0.95
            exec_price = round(exec_price, 1) # Rounding should ideally use exchange meta
            
            # Construct Payload for Frontend
            # This matches what Hyperliquid SDK expects or what the Frontend needs to call the SDK
            payload = {
                "coin": order.symbol,
                "is_buy": is_buy,
                "sz": order.size,
                "limit_px": exec_price,
                "order_type": {"limit": {"tif": "Ioc"}},
                "reduce_only": order.reduce_only
            }
            
            # Return PENDING_SIGNATURE status with the payload in error_message (or we should add a field to OrderResult)
            # Since OrderResult definition is fixed in schemas.py, we'll use a convention or update schema.
            # For now, let's assume the caller (BotManager) handles the 'PENDING' status and extracts data.
            # We will return the payload as a JSON string in 'order_id' or handle it in BotManager.
            # Better: BotManager broadcasts the OrderRequest directly.
            
            # We return "PENDING" and the BotManager will know to broadcast the request.
            return OrderResult(
                order_id="WAITING_FOR_SIGNATURE",
                status="PENDING",
                filled_size=0.0,
                filled_price=0.0,
                payload=payload
            )
                
        except Exception as e:
            logger.error(f"Order Preparation Exception: {e}")
            return OrderResult(order_id="", status="FAILED", error_message=str(e))

    async def cancel_order(self, order_id: str, symbol: str) -> OrderResult:
        """
        Constructs cancel payload.
        """
        payload = {
            "type": "cancel",
            "coin": symbol,
            "oid": int(order_id)
        }
        return OrderResult(
            order_id=order_id,
            status="PENDING",
            payload=payload
        )

    async def close_all_positions(self) -> List[OrderResult]:
        """
        Generates MARKET SELL payloads for all open positions.
        """
        state = await self.get_portfolio_state()
        results = []
        
        for pos in state.positions:
            if pos.size > 0:
                # Create Market Sell Order
                # We use a very low price for market sell or handle it as market in frontend
                # For safety, we'll use a limit price far below current price if we had it, 
                # but since we don't have price feed here easily, we rely on Frontend 'Market' flag 
                # or send a Market Order payload if supported.
                # Hyperliquid SDK 'market_open' is actually a limit IOC with aggressive price.
                
                # We will construct a payload that implies "Close This Position"
                # The frontend will interpret this.
                
                payload = {
                    "coin": pos.symbol,
                    "is_buy": False, # Sell to close Long
                    "sz": pos.size,
                    "limit_px": 0, # Market
                    "order_type": {"limit": {"tif": "Ioc"}}, # Will need to be adjusted by frontend for Market
                    "reduce_only": True
                }
                
                results.append(OrderResult(
                    order_id="WAITING_FOR_SIGNATURE",
                    status="PENDING",
                    filled_size=0.0,
                    filled_price=0.0,
                    payload=payload
                ))
        
        return results
