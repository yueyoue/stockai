import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import redis

DB_URL = "postgresql+asyncpg://stock:Stock%40123456@127.0.0.1:5432/stockai"

async def test_db():
    engine = create_async_engine(DB_URL)
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        print("DB OK:", result.scalar())
    await engine.dispose()

def test_redis():
    r = redis.Redis(host="127.0.0.1", port=6379, password="Redis@67890")
    print("Redis OK:", r.ping())

asyncio.run(test_db())
test_redis()
