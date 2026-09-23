## 2025-05-18 - Batch SQLite operations in polling loop
**Learning:** Checking and saving individual ads inside the monitoring loop opened and closed SQLite connections N times per poll cycle, causing disk I/O overhead.
**Action:** Use batch query functions (`WHERE ad_id IN (...)`) and `executemany` transactions to check and save multiple items in a single DB connection per cycle.
