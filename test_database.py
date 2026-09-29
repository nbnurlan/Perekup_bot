import os
import sqlite3
import pytest
import config
from database import init_db, is_new_ad, save_ad, get_seen_ad_ids, save_ads, cleanup_old_ads

@pytest.fixture(autouse=True)
def temp_db(tmp_path, monkeypatch):
    """Use a temporary database for each test."""
    db_file = str(tmp_path / "test_olx_ads.db")
    monkeypatch.setattr(config, "DB_PATH", db_file)
    monkeypatch.setattr("database.DB_PATH", db_file)
    init_db()
    yield db_file


def test_is_new_ad_and_save_ad():
    assert is_new_ad("ad_101") is True
    save_ad("ad_101")
    assert is_new_ad("ad_101") is False


def test_get_seen_ad_ids_empty():
    assert get_seen_ad_ids([]) == set()
    assert get_seen_ad_ids(["ad_1", "ad_2"]) == set()


def test_get_seen_ad_ids_and_save_ads():
    save_ads(["ad_1", "ad_2", "ad_3"])

    seen = get_seen_ad_ids(["ad_1", "ad_2", "ad_4", "ad_5"])
    assert seen == {"ad_1", "ad_2"}

    # Ignore duplicates gracefully
    save_ads(["ad_2", "ad_3", "ad_4"])
    seen_updated = get_seen_ad_ids(["ad_1", "ad_2", "ad_3", "ad_4", "ad_5"])
    assert seen_updated == {"ad_1", "ad_2", "ad_3", "ad_4"}


def test_cleanup_old_ads():
    save_ads(["ad_recent", "ad_old"])

    # Manually backdate ad_old in DB
    with sqlite3.connect(config.DB_PATH) as conn:
        conn.execute(
            "UPDATE seen_ads SET seen_at = datetime('now', '-31 days') WHERE ad_id = 'ad_old'"
        )
        conn.commit()

    deleted_count = cleanup_old_ads(days=30)
    assert deleted_count == 1

    assert is_new_ad("ad_old") is True
    assert is_new_ad("ad_recent") is False
