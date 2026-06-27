import asyncio
import time
import os
import sys
from pathlib import Path

# Ensure we can import from backend
sys.path.insert(0, str(Path(__file__).parent.parent))
from backend.database import Database

async def main():
    if os.path.exists("test.db"):
        os.remove("test.db")

    db = Database("test.db")
    await db.initialize()
    await db.ensure_default_campaign()

    start = time.time()
    for _ in range(100):
        await db.get_campaign(None) # Testing the temporal query
    end = time.time()
    print(f"Async execution time: {end - start:.4f}s")

    await db.close()

if __name__ == "__main__":
    asyncio.run(main())
