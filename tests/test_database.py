import os
import sqlite3
import pytest
import database
import config
from database import init_db, is_new_ad, save_ad, filter_new_ad_ids, save_ads, cleanup_old_ads

TEST_DB = "test_olx_ads.db"

@pytest.fixture(autouse=True)
def setup_test_db(monkeypatch):
    monkeypatch.setattr(config, "DB_PATH", TEST_DB)
    monkeypatch.setattr(database, "DB_PATH", TEST_DB)
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    init_db()
    yield
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

def test_single_ad_operations():
    assert is_new_ad("ad_1") is True
    save_ad("ad_1")
    assert is_new_ad("ad_1") is False

def test_batch_ad_operations():
    ad_ids = ["ad_10", "ad_11", "ad_12"]

    # Empty list check
    assert filter_new_ad_ids([]) == set()

    # All are new initially
    new_ids = filter_new_ad_ids(ad_ids)
    assert new_ids == {"ad_10", "ad_11", "ad_12"}

    # Batch save
    save_ads(["ad_10", "ad_11"])

    # Filter after saving two
    remaining_new_ids = filter_new_ad_ids(ad_ids)
    assert remaining_new_ids == {"ad_12"}

    assert is_new_ad("ad_10") is False
    assert is_new_ad("ad_11") is False
    assert is_new_ad("ad_12") is True
