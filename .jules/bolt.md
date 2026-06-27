## 2024-05-24 - Database Indexes for Temporal Queries
**Learning:** SQLite tables (like `campaigns` and `characters`) frequently queried using `ORDER BY created_at DESC LIMIT 1` for the most recent entries suffer from O(n) full table scans if the temporal column is not indexed.
**Action:** When creating new tables that expect to fetch the "latest" record based on a timestamp, always include a `CREATE INDEX` for the timestamp column.
