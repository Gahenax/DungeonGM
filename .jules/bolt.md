## 2024-07-04 - SQLite Temporal Query Performance
**Learning:** Querying SQLite tables for the most recent entry using `ORDER BY created_at DESC LIMIT 1` without a corresponding index on the `created_at` column results in O(N) full table scans. This became a noticeable bottleneck when frequently accessing current campaigns or characters.
**Action:** Always ensure a temporal database index is created (e.g., `CREATE INDEX IF NOT EXISTS idx_table_created_at ON table(created_at DESC)`) when adding or modifying tables that are frequently queried for their most recent entry.
