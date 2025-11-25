import pytest
from unittest.mock import MagicMock, patch
import sys
import os

# Add the backend directory to sys.path to allow imports from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.domain.risk import RiskManager
from app.domain.execution import OrderExecutor

@pytest.fixture
def mock_settings():
    with patch("app.domain.execution.settings") as mock:
        mock.HYPERLIQUID_ENV = "TESTNET"
        mock.PRIVATE_KEY = "0x0000000000000000000000000000000000000000000000000000000000000001"
        mock.SYMBOL = "ETH"
        yield mock

@pytest.fixture
def risk_manager():
    return RiskManager()

@pytest.fixture
def mock_info():
    with patch("app.domain.execution.Info") as mock:
        yield mock

@pytest.fixture
def order_executor(mock_settings, mock_info):
    # We need to mock Account.from_key to avoid actual key processing issues with dummy key
    with patch("app.domain.execution.Account.from_key") as mock_account:
        mock_account.return_value.address = "0xTestAddress"
        executor = OrderExecutor()
        executor.info = mock_info.return_value
        return executor
