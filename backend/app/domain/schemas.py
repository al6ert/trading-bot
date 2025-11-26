from enum import Enum
from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class TradeAction(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

class MarketRegime(str, Enum):
    BULL = "BULL"
    BEAR = "BEAR"
    SIDEWAYS = "SIDEWAYS"

class Candle(BaseModel):
    timestamp: int  # Unix ms
    open: float
    high: float
    low: float
    close: float
    volume: float
    symbol: str
    state: Optional[Literal["bull", "bear", "chop"]] = "chop"

    model_config = ConfigDict(frozen=True)

class Position(BaseModel):
    symbol: str
    side: Literal["LONG", "SHORT"]
    size: float
    entry_price: float
    unrealized_pnl: float = 0.0
    leverage: float = 1.0

class PortfolioState(BaseModel):
    total_equity: float
    available_balance: float
    positions: List[Position] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class TradingSignal(BaseModel):
    symbol: str
    action: TradeAction
    price: float
    confidence: float = Field(ge=0.0, le=1.0)
    regime: MarketRegime
    metadata: dict = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class OrderRequest(BaseModel):
    symbol: str
    action: TradeAction
    size: float
    price: Optional[float] = None
    order_type: Literal["MARKET", "LIMIT"] = "MARKET"
    reduce_only: bool = False

class OrderResult(BaseModel):
    order_id: str
    status: Literal["FILLED", "FAILED", "PENDING"]
    filled_price: Optional[float] = None
    filled_size: Optional[float] = None
    error_message: Optional[str] = None
    filled_size: Optional[float] = None
    error_message: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None

class BenchmarkMetric(BaseModel):
    asset: str
    roi: float
    color: str

class SessionMetric(BaseModel):
    label: str
    value: str
    status: Literal["good", "warning", "danger", "neutral"]

