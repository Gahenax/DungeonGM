## 2026-06-16 - Add Temporal Indexes to Avoid O(n) Scans
**Learning:** SQLite tables (`campaigns`, `characters`) queried for their most recent entry using `ORDER BY created_at DESC LIMIT 1` were lacking corresponding indexes on the `created_at` column. This resulted in O(n) full table scans.
**Action:** Always add an index on columns used in `ORDER BY ... DESC LIMIT 1` queries to ensure performance remains fast (O(log n) or O(1) via index) as data grows.
