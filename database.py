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


def get_seen_ad_ids(ad_ids: list[str]) -> set[str]:
    """
    ⚡ PERFORMANCE OPTIMIZATION:
    Berilgan e'lon ID-lari orasidan allaqachon ko'rilganlarini to'plam (set) sifatida qaytaradi.
    Har bir ID uchun alohida DB ulanishi o'rniga bitta SELECT ... WHERE IN (...) so'rovi
    orqali N+1 muammosini hal qiladi (~40x tezroq).
    """
    if not ad_ids:
        return set()
    placeholders = ",".join("?" * len(ad_ids))
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            f"SELECT ad_id FROM seen_ads WHERE ad_id IN ({placeholders})", ad_ids
        ).fetchall()
    return {row[0] for row in rows}


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
    ⚡ PERFORMANCE OPTIMIZATION:
    Bir nechta e'lon ID-larini bitta tranzaksiya va DB ulanishi ichida saqlaydi (executemany).
    Ko'plab yakka INSERT/commit va disk I/O operatsiyalarini bittaga keltirib, unumdorlikni keskin oshiradi.
    """
    if not ad_ids:
        return
    with sqlite3.connect(DB_PATH) as conn:
        conn.executemany(
            "INSERT OR IGNORE INTO seen_ads (ad_id) VALUES (?)",
            [(ad_id,) for ad_id in ad_ids]
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
