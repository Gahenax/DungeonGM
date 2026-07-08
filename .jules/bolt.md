## 2024-07-08 - Optimize Latest Entry Database Queries

**Learning:** When querying SQLite tables for the most recent entry using `ORDER BY created_at DESC LIMIT 1`, the database performs a full table scan O(n) without an index. This scales poorly as campaign and character records accumulate.
**Action:** Always create a corresponding `CREATE INDEX IF NOT EXISTS` on the temporal column (`created_at`) when implementing tables that are frequently queried for the latest entry to ensure O(1) or O(log n) lookup times.
