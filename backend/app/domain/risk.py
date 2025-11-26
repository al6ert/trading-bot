import logging
from app.core.config import settings
from app.domain.schemas import TradingSignal, PortfolioState, TradeAction, MarketRegime
from app.domain.interfaces import IRiskManager

logger = logging.getLogger(__name__)

class RiskManager(IRiskManager):
    def __init__(self):
        self.max_drawdown_daily = 0.02  # 2% max daily loss
        self.min_liquidity_reserve = 0.20 # Default 20% USDC reserve
        self.btc_lock_pct = 0.0 # Default 0% BTC lock
        self.leverage_limit = 1.0 # Strict 1x

    def update_allocation(self, usdc_lock: float, btc_lock: float):
        """Updates the safety locks (percentages 0-100)"""
        self.min_liquidity_reserve = usdc_lock / 100.0
        self.btc_lock_pct = btc_lock / 100.0
        logger.info(f"🛡️ Risk Settings Updated: USDC Lock={usdc_lock}%, BTC Lock={btc_lock}%")

    async def validate(self, signal: TradingSignal, portfolio: PortfolioState) -> bool:
        """
        Validates if a trade signal can be executed based on risk rules.
        """
        if signal.action == TradeAction.HOLD:
            return False
            
        logger.info(f"🛡️ SENTINEL: Validating {signal.action} signal for {signal.symbol}...")
        
        # Rule 1: Max Drawdown Check (Mocked for MVP)
        # In a real system, we would check today's starting balance vs current.
        # if current_equity < start_equity * (1 - self.max_drawdown_daily):
        #     logger.warning("⛔ RISK: Max daily drawdown reached. Trading halted.")
        #     return False

        # Rule 2: Liquidity Reserve (For BUY orders)
        if signal.action == TradeAction.BUY:
            # Calculate required reserve
            reserve_amount = portfolio.total_equity * self.min_liquidity_reserve
            
            if portfolio.available_balance < reserve_amount:
                logger.warning(f"⛔ RISK: Insufficient liquidity reserve. Available: {portfolio.available_balance}, Required: {reserve_amount}")
                return False

        # Rule 3: BTC Lock (For SELL orders)
        if signal.action == TradeAction.SELL and signal.symbol == "BTC":
            # Calculate minimum BTC value to keep
            min_btc_value = portfolio.total_equity * self.btc_lock_pct
            
            # Estimate current BTC value (using signal price as proxy)
            current_btc_size = sum(p.size for p in portfolio.positions if p.symbol == "BTC")
            current_btc_value = current_btc_size * signal.price
            
            # Calculate value after sell
            # We don't know exact size here yet (it's calculated in calculate_size), 
            # but we can check if we are already below or near limit.
            # Ideally, calculate_size should also respect this.
            
            if current_btc_value <= min_btc_value:
                 logger.warning(f"⛔ RISK: BTC Lock Active. Current Value: {current_btc_value}, Required Lock: {min_btc_value}")
                 return False

        # Rule 4: Leverage Check (Always 1x)
        # Implicitly handled by sizing logic, but good to keep in mind.
        
        logger.info("✅ SENTINEL: Signal Approved.")
        return True

    async def calculate_size(self, signal: TradingSignal, portfolio: PortfolioState) -> float:
        """
        Calculates the amount of asset to buy/sell to maintain 1x leverage.
        Respects Macro Regime Allocation (80% Bull / 20% Bear).
        """
        # Determine Target Allocation based on Signal Regime
        max_crypto_pct = 0.80 if signal.regime == MarketRegime.BULL else 0.20
        
        # Calculate Max Crypto Value allowed
        max_crypto_value = portfolio.total_equity * max_crypto_pct
        
        # Check current exposure
        # For MVP, we assume 'positions' list contains our exposure.
        # We need to sum up the value of current positions.
        current_position_value = 0.0
        for pos in portfolio.positions:
            # Assuming position size is in base asset (e.g. BTC) and we have entry_price
            # Ideally we should use Mark Price here, but entry_price is a proxy if mark not available
            # Or we can use signal.price as current market price approximation
            current_position_value += pos.size * signal.price 

        # Calculate how much more we can buy
        remaining_capacity = max(0, max_crypto_value - current_position_value)
        
        # We can only buy with available USDC, but capped by remaining capacity
        tradeable_usdc = min(portfolio.available_balance, remaining_capacity)
        
        if tradeable_usdc <= 0:
            logger.info(f"⛔ RISK: Allocation Limit Reached. Regime: {signal.regime} (Max {max_crypto_pct*100}%)")
            return 0.0
            
        # Size in Base Currency (e.g. BTC)
        if signal.price <= 0:
            logger.error("Invalid price in signal")
            return 0.0

        size_asset = tradeable_usdc / signal.price
        
        # Rounding (Hyperliquid specific logic should ideally be in Executor or Config, 
        # but generic rounding here is safe for now)
        return round(size_asset, 5)
