import pytest
from app.domain.risk import RiskManager

def test_validate_signal_hold(risk_manager):
    signal = {'action': 'HOLD'}
    state = {'total_equity': 1000.0, 'available_balance': 1000.0}
    assert risk_manager.validate_signal(signal, state) is False

def test_validate_signal_buy_sufficient_liquidity(risk_manager):
    # Reserve is 20% (200). Available is 1000. Should pass.
    signal = {'action': 'BUY'}
    state = {'total_equity': 1000.0, 'available_balance': 1000.0}
    assert risk_manager.validate_signal(signal, state) is True

def test_validate_signal_buy_insufficient_liquidity(risk_manager):
    # Reserve is 20% (200). Available is 100. Should fail.
    signal = {'action': 'BUY'}
    state = {'total_equity': 1000.0, 'available_balance': 100.0}
    assert risk_manager.validate_signal(signal, state) is False

def test_calculate_position_size_bull_mode(risk_manager):
    # Bull mode: 80% crypto. Equity 1000 -> Max Crypto 800.
    # Current pos 0. Available 1000.
    # Can buy 800.
    # Price 2000. Size = 800 / 2000 = 0.4 BTC
    state = {'total_equity': 1000.0, 'available_balance': 1000.0, 'positions': []}
    signal = {'regime': 'BULL'}
    price = 2000.0
    size = risk_manager.calculate_position_size(state, price, signal)
    assert size == 0.4

def test_calculate_position_size_bear_mode(risk_manager):
    # Bear mode: 20% crypto. Equity 1000 -> Max Crypto 200.
    # Current pos 0. Available 1000.
    # Can buy 200.
    # Price 2000. Size = 200 / 2000 = 0.1 BTC
    state = {'total_equity': 1000.0, 'available_balance': 1000.0, 'positions': []}
    signal = {'regime': 'BEAR'}
    price = 2000.0
    size = risk_manager.calculate_position_size(state, price, signal)
    assert size == 0.1

def test_calculate_position_size_capped_by_balance(risk_manager):
    # Bull mode: Max Crypto 800.
    # Available only 100.
    # Can buy 100.
    # Price 100. Size = 1.0
    state = {'total_equity': 1000.0, 'available_balance': 100.0, 'positions': []}
    signal = {'regime': 'BULL'}
    price = 100.0
    size = risk_manager.calculate_position_size(state, price, signal)
    assert size == 1.0
