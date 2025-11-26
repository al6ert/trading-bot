from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from datetime import datetime

from contextlib import asynccontextmanager
# from app.infrastructure.database.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # await init_db()
    yield

app = FastAPI(
    title="Hyperliquid Trader Bot",
    description="Automated Trading System for Hyperliquid Spot",
    version="0.1.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.core.bot import BotManager
from app.api import api_v2

bot = BotManager()

app.include_router(api_v2.router, prefix="/api/v2", tags=["v2"])

@app.get("/")
async def root():
    return {
        "status": "online",
        "env": settings.HYPERLIQUID_ENV,
        "message": "Trader Bot is running"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/start")
async def start_bot():
    return bot.start()

@app.post("/stop")
async def stop_bot():
    return bot.stop()

@app.get("/status")
async def get_status():
    return await bot.get_status()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.API_HOST, port=settings.API_PORT, reload=True)
