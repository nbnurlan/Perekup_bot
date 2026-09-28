# ================================================================
#  database.py — SQLite bilan ishlash
#  Faqat e'lon ID-larini saqlaydi (takrorlanishni oldini olish)
# ================================================================

import sqlite3
import logging
from config import DB_PATH

logger = logging.getLogger(__name__)


def init_db() -> None:
    """
    Bazani yaratadi (agar mavjud bo'lmasa).
    Dastur ishga tushganda bir marta chaqiriladi.
    """
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS seen_ads (
                ad_id   TEXT PRIMARY KEY,
                seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Eski yozuvlarni o'chirish uchun (30 kundan eski)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_seen_at ON seen_ads(seen_at)
        """)
        conn.commit()
    logger.info("✅ Ma'lumotlar bazasi tayyor: %s", DB_PATH)


def is_new_ad(ad_id: str) -> bool:
    """
    E'lon yangi ekanini tekshiradi.
    Yangi bo'lsa — True, allaqachon ko'rilgan bo'lsa — False qaytaradi.
    """
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT 1 FROM seen_ads WHERE ad_id = ?", (ad_id,)
        ).fetchone()
    return row is None


def filter_new_ad_ids(ad_ids: list[str]) -> set[str]:
    """
    Optimization: Batches multiple ad ID existence checks into a single query.
    Reduces DB connection open/close overhead from O(N) to O(1).
    Returns a set of ad_ids that are NEW (i.e. not yet seen in the database).
    """
    if not ad_ids:
        return set()

    with sqlite3.connect(DB_PATH) as conn:
        placeholders = ",".join("?" for _ in ad_ids)
        query = f"SELECT ad_id FROM seen_ads WHERE ad_id IN ({placeholders})"
        existing_rows = conn.execute(query, ad_ids).fetchall()
        existing_ids = {row[0] for row in existing_rows}

    return set(ad_ids) - existing_ids


def save_ad(ad_id: str) -> None:
    """
    E'lon ID-sini bazaga saqlaydi (ko'rildi deb belgilaydi).
    """
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT OR IGNORE INTO seen_ads (ad_id) VALUES (?)", (ad_id,)
        )
        conn.commit()


def save_ads(ad_ids: list[str]) -> None:
    """
    Optimization: Batch inserts multiple ad IDs into the database in a single transaction.
    Significantly reduces I/O disk sync overhead compared to individual INSERT calls in a loop.
    """
    if not ad_ids:
        return

    records = [(ad_id,) for ad_id in ad_ids]
    with sqlite3.connect(DB_PATH) as conn:
        conn.executemany(
            "INSERT OR IGNORE INTO seen_ads (ad_id) VALUES (?)", records
        )
        conn.commit()


def cleanup_old_ads(days: int = 30) -> int:
    """
    N kundan eski yozuvlarni o'chiradi (baza kattalashib ketmasligi uchun).
    O'chirilgan yozuvlar sonini qaytaradi.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "DELETE FROM seen_ads WHERE seen_at < datetime('now', ? || ' days')",
            (f"-{days}",)
        )
        conn.commit()
        deleted = cursor.rowcount
    if deleted:
        logger.info("🗑️ Eski yozuvlar tozalandi: %d ta", deleted)
    return deleted
