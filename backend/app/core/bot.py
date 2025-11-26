import asyncio
import logging
from typing import List, Dict, Any
from app.domain.strategies.dual_core import StrategyEngine
from app.domain.risk import RiskManager
from app.domain.execution import OrderExecutor
from app.domain.schemas import TradeAction, OrderRequest, PortfolioState, Candle
from app.infrastructure.hyperliquid.stream import HyperliquidStream
from app.core.websocket import manager

logger = logging.getLogger(__name__)

class BotManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BotManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        self.strategy = StrategyEngine()
        self.risk = RiskManager()
        self.executor = OrderExecutor()
        
        # Initialize Stream with callbacks
        self.stream = HyperliquidStream(
            on_candle=self._on_candle,
            on_user_event=self._on_user_event
        )
        self.stream_task = None
        
        self.running = False
        self.task = None
        self.logs: List[str] = []
        self.portfolio: Dict[str, Any] = {}
        
        self._initialized = True
        logger.info("🤖 BotManager Initialized")

    def start(self):
        if self.running:
            return {"status": "already_running"}
            
        self.running = True
        self.task = asyncio.create_task(self._loop())
        self.stream_task = asyncio.create_task(self.stream.connect())
        self._log("🚀 Strategy Engine & Stream Started")
        return {"status": "started"}

    def stop(self):
        if not self.running:
            return {"status": "already_stopped"}
            
        self.running = False
        if self.task:
            self.task.cancel()
        
        if self.stream:
            self.stream.stop()
        if self.stream_task:
            self.stream_task.cancel()
            
        self._log("🛑 Strategy Engine & Stream Stopped")
        return {"status": "stopped"}

    async def get_status(self):
        # Update portfolio snapshot if possible
        try:
            # Now async
            portfolio_state = await self.executor.get_portfolio_state()
            self.portfolio = portfolio_state.model_dump()
        except Exception as e:
            logger.error(f"Error fetching portfolio for status: {e}")

        return {
            "running": self.running,
            "logs": self.logs[-50:], # Return last 50 logs
            "portfolio": self.portfolio,
        }

    def _log(self, message: str):
        logger.info(message)
        self.logs.append(message)
        if len(self.logs) > 100:
            self.logs.pop(0)
        
        # Broadcast via WS
        try:
            loop = asyncio.get_running_loop()
            if loop.is_running():
                loop.create_task(manager.broadcast({
                    "type": "log",
                    "data": message,
                    "timestamp": asyncio.get_event_loop().time()
                }))
        except RuntimeError:
            pass

    async def _on_candle(self, candle: Candle):
        """Callback for new candles from stream"""
        # Broadcast to Frontend
        try:
            await manager.broadcast({
                "type": "candle",
                "data": candle.model_dump(),
                "timestamp": asyncio.get_event_loop().time()
            })
            # Optionally trigger strategy here in the future
            # await self.strategy.analyze([candle], ...) 
        except Exception as e:
            logger.error(f"Error in _on_candle: {e}")

    async def _on_user_event(self, event: dict):
        """Callback for user events (fills, etc)"""
        self._log(f"🔔 User Event: {event}")
        try:
            await manager.broadcast({
                "type": "user_event",
                "data": event,
                "timestamp": asyncio.get_event_loop().time()
            })
            # Refresh portfolio state immediately
            portfolio_state = await self.executor.get_portfolio_state()
            self.portfolio = portfolio_state.model_dump()
            await manager.broadcast({
                "type": "portfolio",
                "data": self.portfolio,
                "timestamp": asyncio.get_event_loop().time()
            })
        except Exception as e:
            logger.error(f"Error in _on_user_event: {e}")

    async def _loop(self):
        self._log("🔄 Bot Loop Active (Interval: 15s)")
        
        while self.running:
            try:
                # 1. Fetch State
                portfolio_state = await self.executor.get_portfolio_state()
                
                # 2. Analyze
                # Strategy fetches its own data internally for now
                signal = await self.strategy.analyze([], portfolio_state)
                
                self._log(f"📊 Analysis: {signal.action} | Regime: {signal.regime} | Conf: {signal.confidence}")
                
                # 3. Validate & Execute
                if signal.action != TradeAction.HOLD:
                    is_valid = await self.risk.validate(signal, portfolio_state)
                    
                    if is_valid:
                        size = await self.risk.calculate_size(signal, portfolio_state)
                        
                        if size > 0:
                            order_req = OrderRequest(
                                symbol=signal.symbol,
                                action=signal.action,
                                size=size,
                                price=signal.price,
                                order_type="MARKET" # Or LIMIT based on strategy
                            )
                            
                            result = await self.executor.execute_order(order_req)
                            
                            if result.status == "FILLED":
                                self._log(f"✅ Executed {signal.action} {size} {signal.symbol}")
                            elif result.status == "PENDING" and result.payload:
                                # Non-Custodial Flow: Broadcast to Frontend for Signing
                                try:
                                    await manager.broadcast({
                                        "type": "ORDER_REQUEST",
                                        "data": result.payload,
                                        "timestamp": asyncio.get_event_loop().time()
                                    })
                                    self._log(f"📝 Signing Request Sent to Frontend: {signal.action} {size} {signal.symbol}")
                                except Exception as e:
                                    self._log(f"❌ Error broadcasting order: {e}")
                            else:
                                self._log(f"❌ Execution Failed: {result.error_message}")
                        else:
                            self._log(f"⚠️ Risk Manager: Size 0 (Alloc Limit or No Cash)")
                    else:
                        self._log(f"🛡️ Risk Manager: Signal Rejected")
                
                # Sleep for 15 seconds (Testnet speed)
                await asyncio.sleep(15)
                
            except asyncio.CancelledError:
                self._log("⚠️ Loop Cancelled")
                break
            except Exception as e:
                logger.error(f"Loop Error: {e}")
                self._log(f"❌ Error: {str(e)}")
                await asyncio.sleep(5)
