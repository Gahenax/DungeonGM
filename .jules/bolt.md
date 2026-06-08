## 2024-06-08 - [Missing Database Indexes for Temporal Queries]
**Learning:** In the SQLite backend, the database frequently queries for the most recent `campaigns` and `characters` using `ORDER BY created_at DESC LIMIT 1`. Without proper indexes on the `created_at` column, this results in O(n) full table scans which can become a significant bottleneck as the tables grow.
**Action:** Added `idx_campaigns_created_at` and `idx_characters_created_at` indexes during table creation to optimize these frequent temporal queries, transforming O(n) table scans into O(1) or O(log n) index lookups.
