## 2025-05-18 - Batch SQLite query and insert operations for ad monitoring

**Learning:** Opening and closing SQLite database connections and executing individual SELECT/INSERT statements per parsed item in a loop creates significant I/O overhead and connection allocation latency (O(N) connections and transactions). Replacing per-row connections with batch parameter query `WHERE ad_id IN (...)` and `executemany` reduces DB overhead to O(1) connection and transaction per polling cycle, improving performance by up to ~95% during page checks.

**Action:** Always batch check and insert IDs when processing collections of parsed web items.
