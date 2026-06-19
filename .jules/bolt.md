## 2024-05-17 - [Database index for ORDER BY timestamp queries]
**Learning:** Found N+1 full table scans in SQLite when querying the most recent entries (e.g. `SELECT * FROM campaigns ORDER BY created_at DESC LIMIT 1`) because of a missing temporal index. SQLite builds a temp B-TREE for the order by.
**Action:** Always create a `CREATE INDEX` on `created_at` (or equivalent timestamp columns) when designing tables whose records are frequently retrieved by their recency.
