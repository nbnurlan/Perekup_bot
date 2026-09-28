import os
import pytest
import sqlite3
import config

# Override DB_PATH for tests
TEST_DB_PATH = "test_olx_ads.db"
config.DB_PATH = TEST_DB_PATH

import database

@pytest.fixture(autouse=True)
def setup_test_db():
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    database.init_db()
    yield
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

def test_is_new_ad_and_save_ad():
    assert database.is_new_ad("ad1") is True
    database.save_ad("ad1")
    assert database.is_new_ad("ad1") is False

def test_filter_new_ad_ids_and_save_ads():
    ad_ids = ["ad1", "ad2", "ad3", "ad4"]

    # Initially all are new
    new_ids = database.filter_new_ad_ids(ad_ids)
    assert new_ids == {"ad1", "ad2", "ad3", "ad4"}

    # Save a batch
    database.save_ads(["ad1", "ad3"])

    # Now ad1 and ad3 should not be in new_ids
    remaining_new = database.filter_new_ad_ids(ad_ids)
    assert remaining_new == {"ad2", "ad4"}

def test_filter_empty_list():
    assert database.filter_new_ad_ids([]) == set()

def test_save_ads_empty():
    database.save_ads([])  # should execute without error

def test_cleanup_old_ads():
    # Insert an old ad manually
    with sqlite3.connect(TEST_DB_PATH) as conn:
        conn.execute(
            "INSERT INTO seen_ads (ad_id, seen_at) VALUES (?, datetime('now', '-35 days'))",
            ("old_ad",)
        )
        conn.execute(
            "INSERT INTO seen_ads (ad_id, seen_at) VALUES (?, datetime('now', '-5 days'))",
            ("recent_ad",)
        )
        conn.commit()

    deleted = database.cleanup_old_ads(days=30)
    assert deleted == 1
    assert database.is_new_ad("old_ad") is True
    assert database.is_new_ad("recent_ad") is False
