from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    HYPERLIQUID_ENV: str = "TESTNET"
    PRIVATE_KEY: Optional[str] = None
    PUBLIC_ADDRESS: Optional[str] = None
    
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    
    # Trading Config
    SYMBOL: str = "BTC"  # User requested BTCUSDT (Hyperliquid uses 'BTC')
    TIMEFRAME: str = "15m" # Default timeframe for strategy

    class Config:
        env_file = ".env"

settings = Settings()
