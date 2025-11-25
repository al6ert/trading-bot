from typing import Protocol, List, Dict, Any
from app.domain.schemas import PortfolioState, TradingSignal, OrderRequest, OrderResult, Candle

class IStrategy(Protocol):
    async def analyze(self, market_data: List[Candle], portfolio: PortfolioState) -> TradingSignal:
        """Analyzes market data and portfolio state to generate a trading signal."""
        ...

class IRiskManager(Protocol):
    async def validate(self, signal: TradingSignal, portfolio: PortfolioState) -> bool:
        """Validates if a signal is safe to execute."""
        ...

    async def calculate_size(self, signal: TradingSignal, portfolio: PortfolioState) -> float:
        """Calculates the safe position size for the trade."""
        ...

class IExecutor(Protocol):
    async def get_portfolio_state(self) -> PortfolioState:
        """Fetches the current state of the portfolio (balances, positions)."""
        ...

    async def execute_order(self, order: OrderRequest) -> OrderResult:
        """Executes an order on the exchange."""
        ...

    async def cancel_order(self, order_id: str, symbol: str) -> OrderResult:
        """Cancels an existing order."""
        ...
