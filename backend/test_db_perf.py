import asyncio
import time
from backend.database import Database

async def main():
    db = Database("test.db")
    await db.initialize()

    start = time.time()
    for _ in range(100):
        await db.get_campaign("campaign_1")
    end = time.time()
    print(f"Async execution time: {end - start:.4f}s")

    await db.close()

if __name__ == "__main__":
    asyncio.run(main())
