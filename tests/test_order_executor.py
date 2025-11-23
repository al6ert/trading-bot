import pytest
from unittest.mock import MagicMock

def test_get_account_state_success(order_executor, mock_exchange):
    # Mock spot_user_state response
    mock_exchange.return_value.info.spot_user_state.return_value = {
        'balances': [{'coin': 'USDC', 'total': '1500.0'}]
    }
    
    # Mock user_state (margin summary) - though code prioritizes spot balances for equity in simplified logic
    mock_exchange.return_value.info.user_state.return_value = {
        'marginSummary': {'accountValue': '1500.0'}
    }

    state = order_executor.get_account_state()
    
    assert state['total_equity'] == 1500.0
    assert state['available_balance'] == 1500.0
    assert len(state['positions']) == 1

def test_get_account_state_error(order_executor, mock_exchange):
    mock_exchange.return_value.info.spot_user_state.side_effect = Exception("API Error")
    
    state = order_executor.get_account_state()
    
    assert state['total_equity'] == 0.0
    assert state['available_balance'] == 0.0
    assert state['positions'] == []

def test_execute_order_buy(order_executor, mock_exchange):
    mock_exchange.return_value.order.return_value = {'status': 'ok', 'oid': 123}
    
    order_executor.execute_order('BUY', 0.1, 2000.0)
    
    # Verify order call
    mock_exchange.return_value.order.assert_called_once()
    call_args = mock_exchange.return_value.order.call_args[1]
    assert call_args['name'] == 'ETH'
    assert call_args['is_buy'] is True
    assert call_args['sz'] == 0.1
    # Price should be 2000 * 1.05 = 2100
    assert call_args['limit_px'] == 2100.0
    assert call_args['order_type'] == {"limit": {"tif": "Ioc"}}

def test_execute_order_sell(order_executor, mock_exchange):
    mock_exchange.return_value.order.return_value = {'status': 'ok', 'oid': 124}
    
    order_executor.execute_order('SELL', 0.5, 2000.0)
    
    # Verify order call
    mock_exchange.return_value.order.assert_called_once()
    call_args = mock_exchange.return_value.order.call_args[1]
    assert call_args['is_buy'] is False
    # Price should be 2000 * 0.95 = 1900
    assert call_args['limit_px'] == 1900.0
