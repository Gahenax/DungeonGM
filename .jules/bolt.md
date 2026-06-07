## 2024-06-07 - Missing Indexes on Temporal Queries
**Learning:** Found N+1-like performance bottleneck in database read operations `get_campaign` and `get_character` where lack of an index on `created_at` forces a full table scan and sort on O(n) queries requesting the most recent entry.
**Action:** Always verify that frequently accessed temporal properties like `created_at` or `updated_at` have database indexes if they are regularly queried to sort records or fetch the latest row.
