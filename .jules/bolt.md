## 2025-02-18 - Batching SQLite Connection and Queries
**Learning:** Checking and saving individual items in a loop with SQLite opens/closes database connections and commits transactions per item (N+1 connection problem), creating severe disk I/O bottlenecks. Batch querying with `WHERE ad_id IN (...)` and batch inserting with `executemany` within a single transaction improved SQLite operation speed by ~40x.
**Action:** Always batch database lookups (`SELECT ... WHERE IN (...)`) and writes (`executemany`) when processing batches of fetched items instead of querying in a loop.
