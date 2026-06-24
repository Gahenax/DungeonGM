## 2024-06-24 - Database Indexes on Temporal Columns
**Learning:** When adding or modifying SQLite tables that are frequently queried for the most recent entry (e.g., using `ORDER BY created_at DESC LIMIT 1`), a corresponding database index on the temporal column is required to prevent O(n) full table scans.
**Action:** Always verify if queries use `ORDER BY [column] DESC LIMIT [n]` and add an index on that column.
