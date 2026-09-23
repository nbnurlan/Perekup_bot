## 2024-05-18 - SQLite Batch Queries in Monitoring Loop
**Learning:** Checking and inserting advertisement IDs individually in a loop creates significant connection/transaction overhead in SQLite ($O(N)$ operations).
**Action:** Use batch SQL queries (`WHERE ad_id IN (...)`) and batch insertions (`executemany`) to collapse loop database operations into $O(1)$ operations per check cycle (~10x-15x faster database execution).
