import asyncio
import time
import os
from backend.database import Database

async def main():
    if os.path.exists("test.db"):
        os.remove("test.db")

    db = Database("test.db")
    await db.initialize()

    # Pre-populate database
    await db.ensure_default_campaign()

    start = time.time()
    for _ in range(100):
        await db.get_campaign("campaign_1")
    end = time.time()
    print(f"Async execution time (indexed): {end - start:.4f}s")

    await db.close()

if __name__ == "__main__":
    asyncio.run(main())
