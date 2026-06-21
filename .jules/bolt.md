## 2024-06-21 - [SQLite Full Table Scans for Temporal Queries]
**Learning:** SQLite backend frequently queries the `campaigns` and `characters` tables for the most recent entry using `ORDER BY created_at DESC LIMIT 1`. Without indices on the `created_at` column, this results in O(n) full table scans, which degrades performance as the number of entries grows.
**Action:** Always ensure a database index on the temporal column is created for tables that are frequently queried for the most recent entry.
