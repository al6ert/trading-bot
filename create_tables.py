import asyncio
from app.infrastructure.database.database import engine, Base
from app.infrastructure.database import models # Import models to register them with Base

async def create_tables():
    async with engine.begin() as conn:
        print("Creating tables...")
        await conn.run_sync(Base.metadata.create_all)
        print("Tables created successfully.")

if __name__ == "__main__":
    asyncio.run(create_tables())
