from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from datetime import datetime
from app.infrastructure.database.database import Base

class PortfolioSnapshot(Base):
    __tablename__ = "portfolio_snapshots"

    # TimescaleDB requires 'time' column as part of the primary key for partitioning
    # We use a composite PK (time, id) or just time if unique enough, but for ORM safety we keep ID.
    # However, for Hypertables, 'time' is the partition key.
    time = Column(DateTime, primary_key=True, default=datetime.utcnow, index=True)
    id = Column(Integer, autoincrement=True) # Optional in pure time-series, but useful for ORM
    
    # Total Portfolio
    total_equity_usd = Column(Float, nullable=False)
    stablecoin_balance = Column(Float, default=0.0)
    
    # Short Term Bag
    short_term_equity_usd = Column(Float, default=0.0)
    short_term_pnl_cumulative = Column(Float, default=0.0)
    
    # Long Term Bag
    long_term_equity_usd = Column(Float, default=0.0)
    long_term_btc_amount = Column(Float, default=0.0)
    
    # Market Data at Snapshot
    btc_price = Column(Float, nullable=False)

class TradeLog(Base):
    __tablename__ = "trade_logs"

    time = Column(DateTime, primary_key=True, default=datetime.utcnow, index=True)
    id = Column(Integer, autoincrement=True)
    
    type = Column(String, index=True) # TRADE, SYSTEM, ERROR, RISK
    message = Column(String, nullable=False)
    metadata_json = Column(JSON, nullable=True)

class MarketCandle(Base):
    __tablename__ = "market_candles"
    
    time = Column(DateTime, primary_key=True, index=True)
    symbol = Column(String, primary_key=True) # Composite PK with time
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=True)
