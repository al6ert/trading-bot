import pytest
from unittest.mock import MagicMock, patch
from app.domain.execution import OrderExecutor
from app.domain.schemas import Position, PortfolioState

@pytest.mark.asyncio
async def test_panic_generates_safe_payloads():
    # 1. Setup Mock Executor with Fake Portfolio
    with patch("app.domain.execution.Info") as mock_info:
        # Mock settings if needed, but OrderExecutor reads it at init.
        # We can just instantiate it.
        
        executor = OrderExecutor()
        executor.info = mock_info.return_value
        
        # Mock get_portfolio_state to return 2 positions
        # We mock the method directly to avoid mocking the Info API call complexity
        with patch.object(executor, 'get_portfolio_state') as mock_get_state:
            mock_get_state.return_value = PortfolioState(
                total_equity=1000.0,
                available_balance=500.0,
                positions=[
                    Position(symbol="ETH", side="LONG", size=1.5, entry_price=2000.0, unrealized_pnl=100.0),
                    Position(symbol="BTC", side="LONG", size=0.1, entry_price=30000.0, unrealized_pnl=50.0)
                ]
            )
            
            # 2. Execute Panic Close
            results = await executor.close_all_positions()
            
            # 3. Verify Results
            assert len(results) == 2
            
            for res in results:
                assert res.status == "PENDING"
                assert res.order_id == "WAITING_FOR_SIGNATURE"
                
                # Verify Payload Security
                payload = res.payload
                
                # CRITICAL SECURITY CHECKS
                assert payload['reduce_only'] == True
                assert payload['is_buy'] == False # Closing Longs means Selling
                assert payload['limit_px'] == 0 # Market Order (or aggressive limit)
                assert payload['sz'] > 0
                
                print(f"✅ Verified Payload for {payload['coin']}: {payload}")
