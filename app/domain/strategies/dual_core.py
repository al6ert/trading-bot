import pandas as pd
import logging
from app.domain.strategies.indicators import Indicators
from app.infrastructure.hyperliquid.ingestor import DataIngestor

logger = logging.getLogger(__name__)

class StrategyEngine:
    def __init__(self):
        self.ingestor = DataIngestor()
        self.indicators = Indicators()
        
    def analyze(self, account_state: dict = None) -> dict:
        """
        Main strategy loop.
        Returns a signal dict: {'action': 'BUY'|'SELL'|'HOLD', 'reason': str, 'confidence': float, 'regime': str}
        """
        # 1. Get Data (Multi-Timeframe)
        # Macro (1d) for Regime
        df_daily = self.ingestor.get_candles(timeframe="1d", limit=210)
        # Super Macro (1w) - User requested
        df_weekly = self.ingestor.get_candles(timeframe="1w", limit=210)
        
        # Context (4h) for Trend Filter
        df_4h = self.ingestor.get_candles(timeframe="4h", limit=50)
        # Execution (15m) for Signals
        df_15m = self.ingestor.get_candles(timeframe="15m", limit=100)
        
        if df_daily.empty or df_15m.empty:
            return {'action': 'HOLD', 'reason': 'No Data', 'confidence': 0.0}
            
        # 2. Macro Regime Selector (The Judge)
        # Calculate 200 EMA on Daily
        df_daily['ema_200'] = self.indicators.ema(df_daily['close'], 200)
        current_daily = df_daily.iloc[-1]
        
        # Determine Regime
        # If price > EMA 200 -> BULL (Target 80% Crypto)
        # If price < EMA 200 -> BEAR (Target 20% Crypto)
        macro_regime = 'BULL' if current_daily['close'] > current_daily['ema_200'] else 'BEAR'
        target_allocation = 0.80 if macro_regime == 'BULL' else 0.20
        
        # Super Macro Check (Weekly)
        if not df_weekly.empty:
            df_weekly['ema_200'] = self.indicators.ema(df_weekly['close'], 200)
            current_weekly = df_weekly.iloc[-1]
            logger.info(f"🌌 SUPER MACRO (1W): Price: {current_weekly['close']} | EMA200: {current_weekly['ema_200']:.2f}")

        logger.info(f"🌍 MACRO REGIME (1D): {macro_regime} (Target Alloc: {target_allocation*100}%) | Price: {current_daily['close']} | EMA200: {current_daily['ema_200']:.2f}")

        # 3. Check for Forced De-risking (Bear Mode)
        if macro_regime == 'BEAR' and account_state:
            # Check current allocation
            total_equity = account_state.get('total_equity', 0.0)
            # Assuming 'position_value' is available or calculated from positions
            # For MVP, let's assume we can get it. If not, we skip this check for now or approximate.
            # Let's assume account_state has 'margin_summary' or we calculate it.
            # Simplified: If we have a position and we are in BEAR mode, we might want to reduce.
            # But "Progressive Sale" is complex. For now, we just enforce the limit on NEW buys.
            # If we want to force sell, we need to generate a SELL signal here.
            pass

        # 4. Calculate Indicators (Execution Timeframe - 15m)
        df = df_15m.copy()
        # Trend
        df['ema_9'] = self.indicators.ema(df['close'], 9)
        df['ema_21'] = self.indicators.ema(df['close'], 21)
        
        # Momentum/Range
        df['rsi'] = self.indicators.rsi(df['close'], 14)
        bb = self.indicators.bollinger_bands(df['close'], 20, 2)
        df = pd.concat([df, bb], axis=1)
        
        # Volatility
        df['adx'] = self.indicators.adx(df['high'], df['low'], df['close'], 14)
        
        current = df.iloc[-1]
        prev = df.iloc[-2]
        
        # 5. Sub-Engine Selection
        is_trending = current['adx'] > 25
        
        signal = {'action': 'HOLD', 'reason': 'Wait', 'confidence': 0.0, 'regime': macro_regime}
        
        if is_trending:
            # --- ENGINE A: TREND (EMA Crossover) ---
            # Bullish Cross
            if prev['ema_9'] <= prev['ema_21'] and current['ema_9'] > current['ema_21']:
                signal = {'action': 'BUY', 'reason': 'Trend: EMA Golden Cross', 'confidence': 0.8, 'regime': macro_regime}
            # Bearish Cross
            elif prev['ema_9'] >= prev['ema_21'] and current['ema_9'] < current['ema_21']:
                signal = {'action': 'SELL', 'reason': 'Trend: EMA Death Cross', 'confidence': 0.8, 'regime': macro_regime}
            else:
                signal = {'action': 'HOLD', 'reason': 'Trend: No Crossover', 'confidence': 0.0, 'regime': macro_regime}
                
        else:
            # --- ENGINE B: RANGE (RSI + Bollinger) ---
            # Oversold + Lower Band Touch -> BUY
            if current['rsi'] < 30 and current['low'] <= current['lower']:
                signal = {'action': 'BUY', 'reason': 'Range: Oversold + BB Touch', 'confidence': 0.7, 'regime': macro_regime}
            # Overbought + Upper Band Touch -> SELL
            elif current['rsi'] > 70 and current['high'] >= current['upper']:
                signal = {'action': 'SELL', 'reason': 'Range: Overbought + BB Touch', 'confidence': 0.7, 'regime': macro_regime}
            else:
                signal = {'action': 'HOLD', 'reason': 'Range: Neutral', 'confidence': 0.0, 'regime': macro_regime}
        
        # 6. Macro Override (Optional but recommended)
        # If BEAR regime, maybe we ignore BUY signals from Range engine?
        # User said: "Los Sub-motores A y B solo operan con ese 20% restante."
        # This implies they CAN operate, but the Risk Manager limits the size.
        # So we don't block the signal here, we let Risk Manager handle the size.
        
        signal['price'] = current['close']
        logger.info(f"Analysis Complete. Price: {current['close']} | ADX: {current['adx']:.2f} | Signal: {signal['action']}")
        return signal
