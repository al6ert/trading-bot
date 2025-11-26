from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import text
from app.core.config import settings

# PostgreSQL + asyncpg connection string
# Ensure you have a local postgres instance running with these credentials or update .env
DATABASE_URL = "postgresql+asyncpg://user:password@localhost/trader_bot"

engine = create_async_engine(
    DATABASE_URL,
    echo=settings.LOG_LEVEL == "DEBUG",
    future=True
)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

async def init_db():
    # Ensure models are imported so they are registered with Base.metadata
    from app.infrastructure.database import models 
    async with engine.begin() as conn:
        # Create tables (standard SQLAlchemy)
        await conn.run_sync(Base.metadata.create_all)
        
        # Execute TimescaleDB setup
        try:
            with open("app/infrastructure/database/init_timescale.sql", "r") as f:
                sql_script = f.read()
                # Execute statements one by one or as a block depending on driver support
                # asyncpg supports executing blocks usually
                await conn.execute(text(sql_script))
        except Exception as e:
            print(f"Warning: Could not execute TimescaleDB script: {e}")
            # This might fail if extension is not installed in Postgres or permissions issue
            pass

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
