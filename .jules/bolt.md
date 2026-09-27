## 2025-05-18 - SQLite N+1 Connection Overhead in Async Polling Loop
**Learning:** Sequential per-item SQLite connections (`SELECT` and `INSERT` per item in a loop) introduce substantial disk and connection setup overhead on every polling cycle (~150ms per batch of 100).
**Action:** Use batch `WHERE ad_id IN (...)` queries (`filter_new_ads`) and `executemany` (`save_ads`) in SQLite to complete lookup and bulk insertion in single transactions (~3ms, 50x speedup).
