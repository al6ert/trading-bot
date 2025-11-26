import pytest
import logging
from app.domain.risk import RiskManager
from app.domain.execution import OrderExecutor
from app.domain.schemas import TradingSignal, TradeAction, MarketRegime, OrderRequest

logger = logging.getLogger(__name__)

@pytest.mark.asyncio
async def test_sentinel_and_executor_integration(mock_settings, mock_info):
    # Setup Mocks
    mock_info.return_value.spot_user_state.return_value = {
        'balances': [{'coin': 'USDC', 'total': '2000.0'}]
    }
    # mock_info does not have order method in the code, OrderExecutor returns PENDING
    # mock_exchange.return_value.order.return_value = {'status': 'ok', 'response': {'oid': 123}}

    logger.info("🛡️  Initializing The Sentinel (Risk Manager)...")
    risk = RiskManager()
    
    logger.info("🔌 Initializing Executor...")
    executor = OrderExecutor()
    # Inject mock exchange manually since we are not using the fixture to inject it into the instance directly in this test setup style
    # But wait, the fixture 'mock_exchange' patches 'app.domain.execution.Exchange'. 
    # So when OrderExecutor() is instantiated, it uses the mock.
    
    # 1. Fetch Account State
    logger.info("Fetching Account State...")
    state = await executor.get_portfolio_state()
    logger.info(f"Account State: {state}")
    
    assert state.total_equity == 2000.0
    
    # 2. Mock a Signal
    price = 2700.0
    mock_signal = TradingSignal(
        symbol="ETH",
        action=TradeAction.BUY,
        price=price,
        confidence=0.9,
        regime=MarketRegime.BEAR,
        metadata={'reason': 'Test Signal'}
    )
    
    # 3. Validate Signal
    logger.info("Validating Mock Signal...")
    is_valid = await risk.validate(mock_signal, state)
    
    if is_valid:
        logger.info("✅ Signal Approved by Sentinel.")
        
        # 4. Calculate Size
        size = await risk.calculate_size(mock_signal, state)
        logger.info(f"Calculated Position Size (BEAR Mode): {size} ETH")
        
        # Bear Mode: 20% of 2000 = 400. 400 / 2700 = 0.14815
        assert size == 0.14815
        
        if size > 0:
            # 5. Execute
            logger.info(f"READY TO EXECUTE: BUY {size} ETH @ ~{price}")
            
            order_req = OrderRequest(
                symbol=mock_signal.symbol,
                action=mock_signal.action,
                size=size,
                price=price
            )
            
            result = await executor.execute_order(order_req)
            assert result.status == "PENDING"
            assert result.order_id == "WAITING_FOR_SIGNATURE"
            assert result.payload is not None
            assert result.payload["sz"] == size
            logger.info(f"Execution Result: {result}")
        else:
            pytest.fail("Size should be > 0")
    else:
        pytest.fail("Signal should be valid")
