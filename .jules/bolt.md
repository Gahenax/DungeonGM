## 2026-06-29 - SQLite Temporal Indexing for O(n) Scan Prevention
**Learning:** SQLite tables (e.g., `campaigns`, `characters`) that are frequently queried for the most recent entry using `ORDER BY created_at DESC LIMIT 1` suffer from O(n) full table scans if the temporal column (`created_at`) lacks an explicit index.
**Action:** When adding or modifying SQLite tables that query by recency, ensure a corresponding database index on the temporal column (e.g., `CREATE INDEX IF NOT EXISTS idx_table_created_at ON table (created_at)`) is created to ensure O(1) or O(log n) lookup efficiency.
