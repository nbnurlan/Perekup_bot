## 2025-05-18 - Batch SQLite Querying for Ad Checks

**Learning:** Checking seen ads one-by-one via individual SQLite `SELECT` calls in a loop creates significant connection/query overhead (~12.8ms for 50 items). Using a single `WHERE ad_id IN (...)` batch query reduces lookup overhead by ~40x down to ~0.3ms.
**Action:** Always batch set membership checks against SQLite tables in loop processing tasks.
