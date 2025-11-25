import pytest
from app.domain.risk import RiskManager
from app.domain.schemas import TradingSignal, PortfolioState, TradeAction, MarketRegime

@pytest.mark.asyncio
async def test_validate_signal_hold(risk_manager):
    signal = TradingSignal(symbol="BTC", action=TradeAction.HOLD, price=100.0, confidence=0.0, regime=MarketRegime.SIDEWAYS)
    state = PortfolioState(total_equity=1000.0, available_balance=1000.0, positions=[])
    result = await risk_manager.validate(signal, state)
    assert result is False

@pytest.mark.asyncio
async def test_validate_signal_buy_sufficient_liquidity(risk_manager):
    # Reserve is 20% (200). Available is 1000. Should pass.
    signal = TradingSignal(symbol="BTC", action=TradeAction.BUY, price=100.0, confidence=0.8, regime=MarketRegime.BULL)
    state = PortfolioState(total_equity=1000.0, available_balance=1000.0, positions=[])
    result = await risk_manager.validate(signal, state)
    assert result is True

@pytest.mark.asyncio
async def test_validate_signal_buy_insufficient_liquidity(risk_manager):
    # Reserve is 20% (200). Available is 100. Should fail.
    signal = TradingSignal(symbol="BTC", action=TradeAction.BUY, price=100.0, confidence=0.8, regime=MarketRegime.BULL)
    state = PortfolioState(total_equity=1000.0, available_balance=100.0, positions=[])
    result = await risk_manager.validate(signal, state)
    assert result is False

@pytest.mark.asyncio
async def test_calculate_position_size_bull_mode(risk_manager):
    # Bull mode: 80% crypto. Equity 1000 -> Max Crypto 800.
    # Current pos 0. Available 1000.
    # Can buy 800.
    # Price 2000. Size = 800 / 2000 = 0.4 BTC
    state = PortfolioState(total_equity=1000.0, available_balance=1000.0, positions=[])
    signal = TradingSignal(symbol="BTC", action=TradeAction.BUY, price=2000.0, confidence=0.8, regime=MarketRegime.BULL)
    size = await risk_manager.calculate_size(signal, state)
    assert size == 0.4

@pytest.mark.asyncio
async def test_calculate_position_size_bear_mode(risk_manager):
    # Bear mode: 20% crypto. Equity 1000 -> Max Crypto 200.
    # Current pos 0. Available 1000.
    # Can buy 200.
    # Price 2000. Size = 200 / 2000 = 0.1 BTC
    state = PortfolioState(total_equity=1000.0, available_balance=1000.0, positions=[])
    signal = TradingSignal(symbol="BTC", action=TradeAction.BUY, price=2000.0, confidence=0.8, regime=MarketRegime.BEAR)
    size = await risk_manager.calculate_size(signal, state)
    assert size == 0.1

@pytest.mark.asyncio
async def test_calculate_position_size_capped_by_balance(risk_manager):
    # Bull mode: Max Crypto 800.
    # Available only 100.
    # Can buy 100.
    # Price 100. Size = 1.0
    state = PortfolioState(total_equity=1000.0, available_balance=100.0, positions=[])
    signal = TradingSignal(symbol="BTC", action=TradeAction.BUY, price=100.0, confidence=0.8, regime=MarketRegime.BULL)
    size = await risk_manager.calculate_size(signal, state)
    assert size == 1.0
