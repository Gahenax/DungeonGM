## 2024-06-22 - [Temporal Indexing for O(log n) Fetch]
**Learning:** SQLite queries like `SELECT * FROM table ORDER BY created_at DESC LIMIT 1` perform an O(n) full table scan without an index. This scales poorly as campaign data and action logs accumulate, creating a noticeable backend bottleneck.
**Action:** Always add an explicit index (e.g., `CREATE INDEX IF NOT EXISTS idx_name ON table (created_at)`) for frequently polled temporal columns to ensure O(log n) fetch times for the most recent entries.
