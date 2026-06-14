## 2024-05-18 - Missing indexes on created_at columns in SQLite
**Learning:** SQLite backend frequently queries `campaigns` and `characters` tables using `ORDER BY created_at DESC LIMIT 1`. Without an index on `created_at`, these operations perform an O(n) full table scan.
**Action:** Add indexes on `created_at` for tables that are frequently queried by temporal recency.
