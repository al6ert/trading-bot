import pytest
from unittest.mock import MagicMock, patch
import pandas as pd
from app.domain.strategies.dual_core import StrategyEngine
from app.domain.schemas import TradeAction, MarketRegime, PortfolioState, TradingSignal

@pytest.fixture
def mock_ingestor():
    with patch("app.domain.strategies.dual_core.DataIngestor") as mock:
        yield mock

@pytest.fixture
def strategy_engine(mock_ingestor):
    return StrategyEngine()

@pytest.mark.asyncio
async def test_strategy_analyze_no_data(strategy_engine, mock_ingestor):
    # Mock empty dataframes
    mock_ingestor.return_value.get_candles.return_value = pd.DataFrame()
    
    portfolio = PortfolioState(total_equity=1000, available_balance=1000, positions=[])
    signal = await strategy_engine.analyze([], portfolio)
    
    assert signal.action == TradeAction.HOLD
    assert signal.metadata["reason"] == "No Data"

@pytest.mark.asyncio
async def test_strategy_analyze_bull_trend(strategy_engine, mock_ingestor):
    # Mock data for Bull Regime and Trend
    # We need to construct dataframes that will trigger specific logic
    # This is complex to mock perfectly with indicators, so we'll mock the internal df logic 
    # or just ensure it runs without crashing and returns a valid signal structure.
    
    # For a unit test, it's better to mock the indicators or provide pre-calculated DFs.
    # But since the strategy calculates indicators internally, we have to provide raw candles 
    # that result in those indicators. That's heavy.
    
    # Alternative: Mock the ingestor to return a DF that has enough rows.
    # We will just verify it returns a TradingSignal object.
    
    # Create a dummy DF with enough rows
    dates = pd.date_range(start='2023-01-01', periods=250, freq='D')
    df = pd.DataFrame({
        'timestamp': dates,
        'open': 100.0,
        'high': 105.0,
        'low': 95.0,
        'close': 100.0,
        'volume': 1000.0
    })
    # Make close price rising to trigger Bull regime (Price > EMA200)
    df['close'] = [100 + i for i in range(250)] 
    
    mock_ingestor.return_value.get_candles.return_value = df
    mock_ingestor.return_value.symbol = "ETH"
    
    portfolio = PortfolioState(total_equity=1000, available_balance=1000, positions=[])
    signal = await strategy_engine.analyze([], portfolio)
    
    assert isinstance(signal, TradingSignal)
    assert signal.regime == MarketRegime.BULL
    # We can't easily assert BUY/SELL without crafting perfect indicator values, 
    # but we assert the structure is correct.
    assert isinstance(signal.action, TradeAction)
