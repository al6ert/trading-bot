from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime, timedelta

from app.infrastructure.database.database import get_db
from app.infrastructure.database.models import PortfolioSnapshot, TradeLog
from app.infrastructure.hyperliquid.client import HyperliquidClient
from app.core.bot import BotManager
from app.core.dummy_data import DummyDataManager

router = APIRouter()
bot = BotManager()
dummy_data = DummyDataManager()
hyperliquid_client = HyperliquidClient()

# --- Cockpit Endpoints ---

@router.get("/status/health")
async def get_health():
    # In a real scenario, check WS connection status here
    return {
        "status": "healthy",
        "latency_ms": 120, # Mock latency
        "ws_connected": True
    }

@router.get("/portfolio/summary")
async def get_portfolio_summary():
    return dummy_data.get_summary()

@router.get("/portfolio/bags")
async def get_portfolio_bags():
    return dummy_data.get_bags()

@router.get("/logs")
async def get_logs(
    limit: int = 50, 
    type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    # Return consistent dummy logs
    logs = dummy_data.get_logs(limit)
    if type and type != "ALL":
        logs = [l for l in logs if l["type"] == type]
    return logs

# --- Analytics Endpoints ---

@router.get("/analytics/equity-curve")
async def get_equity_curve(timeframe: str = "6m", db: AsyncSession = Depends(get_db)):
    return dummy_data.get_equity_curve()

@router.get("/analytics/composition")
async def get_composition(timeframe: str = "6m", db: AsyncSession = Depends(get_db)):
    return dummy_data.get_composition()

@router.get("/analytics/performance/short-term")
async def get_short_term_performance(db: AsyncSession = Depends(get_db)):
    return dummy_data.get_short_term_performance()

@router.get("/analytics/performance/long-term")
async def get_long_term_performance(db: AsyncSession = Depends(get_db)):
    return dummy_data.get_long_term_performance()

# --- Market Data Endpoints ---

@router.get("/market/candles")
def get_candles(timeframe: str = "1h", start: Optional[int] = None, end: Optional[int] = None):
    # Map timeframe to Hyperliquid format if needed, or pass directly
    # Hyperliquid supports: 15m, 1h, 4h, 1d, etc.
    
    # Default symbol for now
    symbol = "BTC" 
    
    candles = hyperliquid_client.get_candles(symbol, timeframe, start, end)
    
    # Transform to frontend format if necessary
    # Hyperliquid returns: {'t': 163..., 'o': '...', 'h': '...', 'l': '...', 'c': '...', 'v': '...'}
    # Frontend expects: { time: number, open: number, high: number, low: number, close: number }
    
    formatted_candles = []
    for c in candles:
        formatted_candles.append({
            "time": int(c['t'] / 1000), # Convert ms to s
            "open": float(c['o']),
            "high": float(c['h']),
            "low": float(c['l']),
            "close": float(c['c'])
        })
        
    return formatted_candles

@router.get("/market/trades")
async def get_trades(db: AsyncSession = Depends(get_db)):
    # Fetch trades from DB
    query = select(TradeLog).where(TradeLog.type == "TRADE").order_by(TradeLog.time.desc()).limit(100)
    result = await db.execute(query)
    trades = result.scalars().all()
    
    # Format for chart markers
    markers = []
    for trade in trades:
        # Parse metadata for details if available
        # Assuming metadata_json contains side, price, etc.
        # Marker format: { time: number, position: 'aboveBar' | 'belowBar', color: string, shape: string, text: string }
        
        try:
            meta = trade.metadata_json or {}
            side = meta.get("side", "BUY") # Default to BUY if unknown, or parse from message
            price = meta.get("price", 0)
            
            # If side is not in metadata, try to guess from message
            if "BUY" in trade.message.upper():
                side = "BUY"
            elif "SELL" in trade.message.upper():
                side = "SELL"
                
            color = "#10b981" if side == "BUY" else "#ef4444"
            position = "belowBar" if side == "BUY" else "aboveBar"
            shape = "arrowUp" if side == "BUY" else "arrowDown"
            
            markers.append({
                "time": int(trade.time.timestamp()),
                "position": position,
                "color": color,
                "shape": shape,
                "text": f"{side} @ {price}"
            })
        except Exception as e:
            continue
            
    return markers

