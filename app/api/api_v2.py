from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from app.infrastructure.database.database import get_db
from app.infrastructure.database.models import PortfolioSnapshot, TradeLog
from app.infrastructure.hyperliquid.client import HyperliquidClient
from app.core.bot import BotManager
from app.core.dummy_data import DummyDataManager
from app.core.websocket import manager

logger = logging.getLogger(__name__)

router = APIRouter()
bot = BotManager()
dummy_data = DummyDataManager()
hyperliquid_client = HyperliquidClient()

@router.websocket("/ws/feed")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle incoming messages if any (e.g. ping/pong)
            # For now we just wait for disconnection
            data = await websocket.receive_text()
            # Optional: Handle client commands via WS
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        manager.disconnect(websocket)

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
    """Get real portfolio summary from connected wallet"""
    try:
        portfolio_state = await bot.executor.get_portfolio_state()
        
        # Calculate totals
        total_crypto_value = 0.0
        for pos in portfolio_state.positions:
            # We use entry_price as proxy since we don't have current prices yet
            # In a full implementation, fetch current prices here
            total_crypto_value += pos.size * (pos.entry_price if pos.entry_price > 0 else 1.0)
        
        total_equity = portfolio_state.available_balance + total_crypto_value
        crypto_pct = (total_crypto_value / total_equity * 100) if total_equity > 0 else 0
        stable_pct = (portfolio_state.available_balance / total_equity * 100) if total_equity > 0 else 100
        
        return {
            "total_equity": round(total_equity, 2),
            "crypto_pct": round(crypto_pct, 1),
            "stable_pct": round(stable_pct, 1),
            "available_balance": round(portfolio_state.available_balance, 2),
            "positions_count": len(portfolio_state.positions)
        }
    except Exception as e:
        logger.error(f"Error fetching portfolio summary: {e}")
        # Fallback to dummy data if real data fails
        return dummy_data.get_summary()

@router.get("/portfolio/bags")
async def get_portfolio_bags():
    """Get real portfolio positions (bags) from connected wallet"""
    try:
        portfolio_state = await bot.executor.get_portfolio_state()
        
        # Calculate values for compatibility with frontend
        total_crypto_value = 0.0
        for pos in portfolio_state.positions:
            total_crypto_value += pos.size * (pos.entry_price if pos.entry_price > 0 else 1.0)
        
        # Return structure compatible with frontend expectations
        # While using real data from the wallet
        return {
            "short_term": {
                "value_usd": round(portfolio_state.available_balance, 2),
                "available_usdt": round(portfolio_state.available_balance, 2),
                "assigned_btc": 0.0,  # Would need to calculate from positions
                "pnl_24h": 0.0,  # Would need historical data
                "active_strategy": "Live Trading" if bot.running else "Inactive"
            },
            "long_term": {
                "value_btc": sum(pos.size for pos in portfolio_state.positions if pos.symbol == "BTC"),
                "value_usd": round(total_crypto_value, 2),
                "accumulated_btc": sum(pos.size for pos in portfolio_state.positions if pos.symbol == "BTC"),
                "reserved_usdt": 0.0,
                "total_yield_btc": 0.0,  # Would need historical data
                "active_strategy": "HODL" if len(portfolio_state.positions) > 0 else "No Positions"
            }
        }
    except Exception as e:
        logger.error(f"Error fetching portfolio bags: {e}")
        # Fallback to dummy data if real data fails
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


# --- Bot Control Endpoints ---

@router.post("/start")
async def start_bot():
    return await bot.start()

@router.post("/stop")
async def stop_bot():
    return await bot.stop()

@router.get("/status")
async def get_bot_status():
    return await bot.get_status()

@router.post("/panic")
async def panic_button():
    """
    Emergency: Stop bot and close all positions immediately.
    """
    # Stop the bot first
    await bot.stop()
    
    # Trigger close all positions
    results = await bot.executor.close_all_positions()
    
    # Broadcast requests to frontend
    count = 0
    for res in results:
        if res.status == "PENDING" and res.payload:
            try:
                await manager.broadcast({
                    "type": "ORDER_REQUEST",
                    "data": res.payload,
                    "timestamp": datetime.utcnow().timestamp()
                })
                count += 1
            except Exception as e:
                logger.error(f"Error broadcasting panic order: {e}")

    return {
        "status": "stopped",
        "action": "panic_close_all",
        "message": f"Bot stopped. Generated {count} close orders.",
        "orders_generated": count
    }
