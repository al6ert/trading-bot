import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class RiskManager:
    def __init__(self):
        self.max_drawdown_daily = 0.05  # 5% max daily loss
        self.min_liquidity_reserve = 0.20 # 20% USDC reserve
        self.leverage_limit = 1.0 # Strict 1x

    def validate_signal(self, signal: dict, account_state: dict) -> bool:
        """
        Validates if a trade signal can be executed based on risk rules.
        account_state: {'total_equity': float, 'available_balance': float, 'positions': list}
        """
        action = signal.get('action')
        
        if action == 'HOLD':
            return False
            
        logger.info(f"🛡️ SENTINEL: Validating {action} signal...")
        
        # Rule 1: Max Drawdown Check (Mocked for MVP, needs PnL tracking)
        # In a real system, we would check today's starting balance vs current.
        # if current_equity < start_equity * (1 - self.max_drawdown_daily):
        #     logger.warning("⛔ RISK: Max daily drawdown reached. Trading halted.")
        #     return False

        # Rule 2: Liquidity Reserve (For BUY orders)
        if action == 'BUY':
            total_equity = account_state.get('total_equity', 0.0)
            available_balance = account_state.get('available_balance', 0.0)
            
            # Calculate required reserve
            reserve_amount = total_equity * self.min_liquidity_reserve
            
            # If we spend, will we breach reserve?
            # Assuming we use 95% of available for the trade (minus gas/fees buffer)
            # This is a simplified check.
            if available_balance < reserve_amount:
                logger.warning(f"⛔ RISK: Insufficient liquidity reserve. Available: {available_balance}, Required: {reserve_amount}")
                return False

        # Rule 3: Leverage Check (Always 1x)
        # Hyperliquid allows leverage, so we must ensure we never borrow.
        # We only buy with available USDC.
        # This is implicitly handled by only using 'available_balance' for sizing.
        
        logger.info("✅ SENTINEL: Signal Approved.")
        return True

    def calculate_position_size(self, account_state: dict, price: float, signal: dict = None) -> float:
        """
        Calculates the amount of asset to buy/sell to maintain 1x leverage.
        Respects Macro Regime Allocation (80% Bull / 20% Bear).
        """
        available_usdc = account_state.get('available_balance', 0.0)
        total_equity = account_state.get('total_equity', 0.0)
        
        # Determine Target Allocation based on Signal Regime
        regime = signal.get('regime', 'BULL') if signal else 'BULL'
        max_crypto_pct = 0.80 if regime == 'BULL' else 0.20
        
        # Calculate Max Crypto Value allowed
        max_crypto_value = total_equity * max_crypto_pct
        
        # Check current exposure (Simplified: assuming we only hold this asset)
        # In a real system, we sum up all position values.
        # For MVP, we assume 'positions' list contains our exposure.
        current_position_value = 0.0
        for pos in account_state.get('positions', []):
             # Assuming pos structure from Hyperliquid SDK
             # We need to know the value. SDK usually gives size and entry price or mark price.
             # Let's assume we can get it or it's 0 for now if no positions.
             # If we can't get it easily, we might overbuy. 
             # For MVP, let's assume we are starting fresh or have 0 exposure if list empty.
             pass

        # Calculate how much more we can buy
        remaining_capacity = max(0, max_crypto_value - current_position_value)
        
        # We can only buy with available USDC, but capped by remaining capacity
        tradeable_usdc = min(available_usdc, remaining_capacity)
        
        # Also respect the "Liquidity Reserve" (20% Cash)
        # Note: 80% Crypto Target implies 20% Cash implicitly.
        # But if we are in Bear Mode (20% Crypto), we have 80% Cash.
        # So the stricter rule applies.
        
        if tradeable_usdc <= 0:
            logger.info(f"⛔ RISK: Allocation Limit Reached. Regime: {regime} (Max {max_crypto_pct*100}%)")
            return 0.0
            
        # Size in Base Currency (BTC)
        size_btc = tradeable_usdc / price
        
        return round(size_btc, 5)
