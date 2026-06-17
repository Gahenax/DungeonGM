## 2024-06-17 - Add indexes on frequently queried fields
**Learning:** Found an N+1 query problem / slow table scan on temporal column in sqlite without an index. The Database class performs `ORDER BY created_at DESC LIMIT 1` frequently. Adding indexes on `campaigns` and `characters` on `created_at DESC` provides a 4x speedup on reads. Also, fixed backend/test_db_perf.py to correctly call asynchronous db methods using asyncio.
**Action:** Always create indexes on columns that are frequently used in `ORDER BY` operations, especially temporal columns like `created_at`.
