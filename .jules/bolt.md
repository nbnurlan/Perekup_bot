## 2025-05-18 - Batch SQLite lookup and save operations
**Learning:** Checking and saving item IDs individually in SQLite loops opens/closes connections and runs transactions per item (O(N) connections & disk commits), creating heavy I/O overhead. Batch querying with `WHERE ad_id IN (...)` and batch inserting with `executemany` reduces I/O to O(1) connections and single transaction commit, yielding >10x speedup.
**Action:** Always batch database lookups (`IN (...)`) and writes (`executemany`) when processing parsed feed items or lists.
