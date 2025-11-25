import pandas as pd
import logging
import asyncio
from typing import List
from app.domain.strategies.indicators import Indicators
from app.infrastructure.hyperliquid.ingestor import DataIngestor
from app.domain.schemas import TradingSignal, PortfolioState, Candle, TradeAction, MarketRegime
from app.domain.interfaces import IStrategy

logger = logging.getLogger(__name__)

class StrategyEngine(IStrategy):
    def __init__(self):
        self.ingestor = DataIngestor()
        self.indicators = Indicators()
        
    async def analyze(self, market_data: List[Candle], portfolio: PortfolioState) -> TradingSignal:
        """
        Main strategy loop.
        Note: 'market_data' argument is kept for interface compliance, but this strategy 
        fetches its own multi-timeframe data via ingestor for now. 
        In a purer architecture, the orchestrator would fetch all data and pass it in.
        """
        # 1. Get Data (Multi-Timeframe) - Async wrapper
        # Macro (1d) for Regime
        df_daily = await asyncio.to_thread(self.ingestor.get_candles, timeframe="1d", limit=210)
        # Super Macro (1w)
        df_weekly = await asyncio.to_thread(self.ingestor.get_candles, timeframe="1w", limit=210)
        
        # Context (4h) for Trend Filter
        df_4h = await asyncio.to_thread(self.ingestor.get_candles, timeframe="4h", limit=50)
        # Execution (15m) for Signals
        df_15m = await asyncio.to_thread(self.ingestor.get_candles, timeframe="15m", limit=100)
        
        if df_daily.empty or df_15m.empty:
            return TradingSignal(
                symbol="UNKNOWN", 
                action=TradeAction.HOLD, 
                price=0.0, 
                confidence=0.0, 
                regime=MarketRegime.SIDEWAYS,
                metadata={"reason": "No Data"}
            )
            
        # 2. Macro Regime Selector (The Judge)
        # Calculate 200 EMA on Daily
        df_daily['ema_200'] = self.indicators.ema(df_daily['close'], 200)
        current_daily = df_daily.iloc[-1]
        
        # Determine Regime
        macro_regime = MarketRegime.BULL if current_daily['close'] > current_daily['ema_200'] else MarketRegime.BEAR
        
        # Super Macro Check (Weekly)
        if not df_weekly.empty:
            df_weekly['ema_200'] = self.indicators.ema(df_weekly['close'], 200)
            current_weekly = df_weekly.iloc[-1]
            logger.info(f"🌌 SUPER MACRO (1W): Price: {current_weekly['close']} | EMA200: {current_weekly['ema_200']:.2f}")

        logger.info(f"🌍 MACRO REGIME (1D): {macro_regime} | Price: {current_daily['close']} | EMA200: {current_daily['ema_200']:.2f}")

        # 3. Calculate Indicators (Execution Timeframe - 15m)
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
        
        # 4. Sub-Engine Selection
        is_trending = current['adx'] > 25
        
        action = TradeAction.HOLD
        reason = "Wait"
        confidence = 0.0
        
        if is_trending:
            # --- ENGINE A: TREND (EMA Crossover) ---
            # Bullish Cross
            if prev['ema_9'] <= prev['ema_21'] and current['ema_9'] > current['ema_21']:
                action = TradeAction.BUY
                reason = 'Trend: EMA Golden Cross'
                confidence = 0.8
            # Bearish Cross
            elif prev['ema_9'] >= prev['ema_21'] and current['ema_9'] < current['ema_21']:
                action = TradeAction.SELL
                reason = 'Trend: EMA Death Cross'
                confidence = 0.8
            else:
                reason = 'Trend: No Crossover'
                
        else:
            # --- ENGINE B: RANGE (RSI + Bollinger) ---
            # Oversold + Lower Band Touch -> BUY
            if current['rsi'] < 30 and current['low'] <= current['lower']:
                action = TradeAction.BUY
                reason = 'Range: Oversold + BB Touch'
                confidence = 0.7
            # Overbought + Upper Band Touch -> SELL
            elif current['rsi'] > 70 and current['high'] >= current['upper']:
                action = TradeAction.SELL
                reason = 'Range: Overbought + BB Touch'
                confidence = 0.7
            else:
                reason = 'Range: Neutral'
        
        current_price = float(current['close'])
        
        logger.info(f"Analysis Complete. Price: {current_price} | ADX: {current['adx']:.2f} | Action: {action}")
        
        return TradingSignal(
            symbol=self.ingestor.symbol,
            action=action,
            price=current_price,
            confidence=confidence,
            regime=macro_regime,
            metadata={"reason": reason, "adx": float(current['adx']), "rsi": float(current['rsi'])}
        )
