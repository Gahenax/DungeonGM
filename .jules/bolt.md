## 2025-02-18 - Avoid O(n) table scans with created_at indexes
**Learning:** In tables like `campaigns` and `characters` where queries frequently fetch the most recently created record using `ORDER BY created_at DESC LIMIT 1`, SQLite will perform an O(n) full table scan if there is no index on the temporal column, causing poor performance as data scales up.
**Action:** Always create a descending index on the temporal column (`CREATE INDEX idx_name ON table(created_at DESC)`) for tables that are frequently queried for the latest entry.
