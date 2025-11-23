import asyncio
import logging
from typing import List, Dict, Any
from app.domain.strategies.dual_core import StrategyEngine
from app.domain.risk import RiskManager
from app.domain.execution import OrderExecutor

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
        self._log("🚀 Strategy Engine Started")
        return {"status": "started"}

    def stop(self):
        if not self.running:
            return {"status": "already_stopped"}
            
        self.running = False
        if self.task:
            self.task.cancel()
        self._log("🛑 Strategy Engine Stopped")
        return {"status": "stopped"}

    def get_status(self):
        # Update portfolio snapshot if possible
        try:
            self.portfolio = self.executor.get_account_state()
        except Exception as e:
            logger.error(f"Error fetching portfolio for status: {e}")

        return {
            "running": self.running,
            "logs": self.logs[-50:], # Return last 50 logs
            "portfolio": self.portfolio,
            # We could also expose current regime/strategy state here if we stored it
        }

    def _log(self, message: str):
        logger.info(message)
        self.logs.append(message)
        if len(self.logs) > 100:
            self.logs.pop(0)

    async def _loop(self):
        self._log("🔄 Bot Loop Active (Interval: 15s)")
        
        while self.running:
            try:
                # 1. Fetch State
                account_state = self.executor.get_account_state()
                
                # 2. Analyze
                # We need to pass account_state to analyze if we want to use it for logic, 
                # but currently analyze fetches its own market data.
                signal = self.strategy.analyze(account_state)
                
                current_price = signal.get('price', 0.0)
                regime = signal.get('regime', 'N/A')
                
                self._log(f"📊 Analysis: {signal['action']} | Regime: {regime} | Conf: {signal['confidence']}")
                
                # 3. Validate & Execute
                if signal['action'] != 'HOLD':
                    if self.risk.validate_signal(signal, account_state):
                        size = self.risk.calculate_position_size(account_state, current_price, signal)
                        
                        if size > 0:
                            self.executor.execute_order(signal['action'], size, current_price)
                            self._log(f"✅ Executed {signal['action']} {size} BTC")
                        else:
                            self._log(f"⚠️ Risk Manager: Size 0 (Alloc Limit or No Cash)")
                    else:
                        self._log(f"🛡️ Risk Manager: Signal Rejected")
                
                # Sleep for 15 seconds (Testnet speed)
                # In production, this might be aligned to candle close.
                await asyncio.sleep(15)
                
            except asyncio.CancelledError:
                self._log("⚠️ Loop Cancelled")
                break
            except Exception as e:
                logger.error(f"Loop Error: {e}")
                self._log(f"❌ Error: {str(e)}")
                await asyncio.sleep(5)
