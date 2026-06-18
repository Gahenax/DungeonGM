## 2024-06-18 - [FastAPI Synchronous Route Handler Optimization]
**Learning:** In the FastAPI backend, computationally-bound, fully synchronous tasks (like `DiceEngine.roll`) mapped to `async def` route handlers will block the single-threaded asyncio event loop, severely degrading concurrent request performance.
**Action:** Always define FastAPI route handlers performing heavy synchronous operations using `def` instead of `async def` so FastAPI can automatically offload them to an external threadpool.
