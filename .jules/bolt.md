## 2024-05-20 - Batching SQLite lookups and inserts
**Learning:** Checking and inserting items individually in SQLite via repeated `sqlite3.connect()` context managers introduces significant connection and commit overhead (~130ms per 100 items). Using batch `SELECT WHERE id IN (...)` (chunked to 500 items to respect SQLite variable limits) and `executemany` reduces execution time to ~2ms (~60x speedup).
**Action:** When working with SQLite in Python loops, always prefer batch `IN` queries and `executemany` over iterative single-record queries.
