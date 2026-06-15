## 2024-05-18 - Missing DB Indexes for Temporal Order Queries
**Learning:** Found an anti-pattern where frequent `ORDER BY created_at DESC LIMIT 1` queries on SQLite tables (`campaigns`, `characters`) caused O(n) full table scans because there were no indexes on `created_at`.
**Action:** Always verify indexes are present for columns used in ORDER BY / LIMIT queries, particularly in tables designed to scale.
