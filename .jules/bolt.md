## 2024-05-18 - SQLite Batch Operations for High-Frequency Polling
**Learning:** Checking/saving items one by one in SQLite incurs N connection/statement overheads and disk sync costs. Replacing individual checks/inserts with single SQL queries (`IN (...)` and `executemany`) reduces database overhead from O(N) to O(1) per polling cycle.
**Action:** When working with SQLite in polling loops, always batch read/write operations into single transactions.
