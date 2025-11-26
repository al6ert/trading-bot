import pytest
from unittest.mock import MagicMock
from app.domain.schemas import TradeAction, OrderRequest, OrderResult, PortfolioState

@pytest.mark.asyncio
async def test_get_portfolio_state_success(order_executor, mock_exchange):
    # Mock spot_user_state response
    # Since we use asyncio.to_thread, the mock will be called in a thread.
    # Standard MagicMock works fine here.
    mock_exchange.return_value.info.spot_user_state.return_value = {
        'balances': [{'coin': 'USDC', 'total': '1500.0'}]
    }
    
    state = await order_executor.get_portfolio_state()
    
    assert isinstance(state, PortfolioState)
    assert state.total_equity == 1500.0
    assert state.available_balance == 1500.0
    assert len(state.positions) == 0

@pytest.mark.asyncio
async def test_get_portfolio_state_error(order_executor, mock_exchange):
    mock_exchange.return_value.info.spot_user_state.side_effect = Exception("API Error")
    
    state = await order_executor.get_portfolio_state()
    
    assert state.total_equity == 0.0
    assert state.available_balance == 0.0
    assert state.positions == []

@pytest.mark.asyncio
async def test_execute_order_buy(order_executor, mock_exchange):
    mock_exchange.return_value.order.return_value = {
        'status': 'ok', 
        'response': {'oid': 123}
    }
    
    order_req = OrderRequest(
        symbol="ETH",
        action=TradeAction.BUY,
        size=0.1,
        price=2000.0
    )
    
    result = await order_executor.execute_order(order_req)
    
    assert isinstance(result, OrderResult)
    assert result.status == "FILLED"
    assert result.order_id == "123"
    
    # Verify order call
    mock_exchange.return_value.order.assert_called_once()
    call_args = mock_exchange.return_value.order.call_args[1]
    assert call_args['name'] == 'ETH'
    assert call_args['is_buy'] is True
    assert call_args['sz'] == 0.1
    # Price should be 2000 * 1.05 = 2100
    assert call_args['limit_px'] == 2100.0
    assert call_args['order_type'] == {"limit": {"tif": "Ioc"}}

@pytest.mark.asyncio
async def test_execute_order_sell(order_executor, mock_exchange):
    mock_exchange.return_value.order.return_value = {
        'status': 'ok', 
        'response': {'oid': 124}
    }
    
    order_req = OrderRequest(
        symbol="ETH",
        action=TradeAction.SELL,
        size=0.5,
        price=2000.0
    )
    
    result = await order_executor.execute_order(order_req)
    
    assert result.status == "FILLED"
    assert result.order_id == "124"
    
    # Verify order call
    mock_exchange.return_value.order.assert_called_once()
    call_args = mock_exchange.return_value.order.call_args[1]
    assert call_args['is_buy'] is False
    # Price should be 2000 * 0.95 = 1900
    assert call_args['limit_px'] == 1900.0
