# Bolt's Journal - Critical Learnings

## 2025-05-10 - Initial Setup
**Learning:** SQLite single connection per query vs batch filtering. In Python sqlite3, opening database connection repeatedly inside a loop for 50 ads creates N connection/statement overheads. Batch querying with `WHERE ad_id IN (...)` or loading recent IDs reduces DB calls from N to 1.
**Action:** Use batch operations (`get_seen_ads(ad_ids)` or `save_ads(ad_ids)`) when checking multiple items at once.
