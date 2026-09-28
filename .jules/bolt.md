## 2025-05-18 - Batch SQLite queries for ad status checks
**Learning:** Checking seen ad IDs individually in a loop creates significant overhead in SQLite by opening/closing connection/transactions N times (~120ms for 50 items vs ~5ms batched). Batching ad ID existence checks into a single `SELECT ... WHERE ad_id IN (...)` query and batch inserting new IDs using `executemany` yields a ~20x+ speedup.
**Action:** Always batch lookups and writes when querying SQLite for lists of parsed items.
