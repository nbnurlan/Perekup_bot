import os
import sqlite3
import pytest

import database


@pytest.fixture(autouse=True)
def temp_db(tmp_path):
    """Use temporary database for tests."""
    db_file = str(tmp_path / "test_olx.db")
    database.DB_PATH = db_file
    database.init_db()
    yield db_file
    if os.path.exists(db_file):
        os.remove(db_file)


def test_is_new_ad_and_save_ad():
    assert database.is_new_ad("ad1") is True
    database.save_ad("ad1")
    assert database.is_new_ad("ad1") is False


def test_get_seen_ads_empty():
    assert database.get_seen_ads([]) == set()


def test_get_seen_ads_and_save_ads():
    ad_ids = ["ad10", "ad20", "ad30"]
    # None seen initially
    assert database.get_seen_ads(ad_ids) == set()

    # Save ad10 and ad30
    database.save_ads(["ad10", "ad30"])

    # Batch query seen ads
    seen = database.get_seen_ads(ad_ids)
    assert seen == {"ad10", "ad30"}

    # Individual queries match
    assert database.is_new_ad("ad10") is False
    assert database.is_new_ad("ad20") is True
    assert database.is_new_ad("ad30") is False


def test_save_ads_duplicates_and_empty():
    database.save_ads([])  # Should handle empty gracefully

    # Duplicate entries in input list
    database.save_ads(["ad50", "ad50", "ad60"])
    assert database.get_seen_ads(["ad50", "ad60"]) == {"ad50", "ad60"}


def test_cleanup_old_ads():
    database.save_ad("recent_ad")
    # Clean up ads older than 30 days
    deleted = database.cleanup_old_ads(days=30)
    assert deleted == 0
    assert database.is_new_ad("recent_ad") is False
