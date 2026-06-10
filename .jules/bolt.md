## 2024-06-10 - Missing Database Indexes on Temporal Columns
**Learning:** The database queries for the most recent campaign and character use `ORDER BY created_at DESC LIMIT 1`. Without an index on `created_at`, SQLite performs a full table scan, resulting in O(n) performance degradation as tables grow.
**Action:** Always ensure a corresponding database index on the temporal column is created when adding or modifying SQLite tables that are frequently queried for the most recent entry.
