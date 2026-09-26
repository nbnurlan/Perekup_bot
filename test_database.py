import sqlite3
import pytest
import config
from database import init_db, is_new_ad, save_ad, filter_new_ad_ids, save_ads, cleanup_old_ads


@pytest.fixture(autouse=True)
def setup_tmp_db(tmp_path, monkeypatch):
    db_file = str(tmp_path / "test_olx.db")
    monkeypatch.setattr(config, "DB_PATH", db_file)
    init_db()
    return db_file


def test_single_ad_operations():
    ad_id = "ID12345"
    assert is_new_ad(ad_id) is True

    save_ad(ad_id)
    assert is_new_ad(ad_id) is False


def test_batch_ad_operations():
    ads = ["ID101", "ID102", "ID103", "ID104"]

    # Initially all should be new
    new_ids = filter_new_ad_ids(ads)
    assert new_ids == set(ads)

    # Save a subset in batch
    save_ads(["ID101", "ID102"])

    # Now filter_new_ad_ids should only return unsaved IDs
    new_ids_after = filter_new_ad_ids(ads)
    assert new_ids_after == {"ID103", "ID104"}

    # Save remaining
    save_ads(["ID103", "ID104"])
    assert filter_new_ad_ids(ads) == set()


def test_filter_empty_list():
    assert filter_new_ad_ids([]) == set()


def test_cleanup_old_ads():
    save_ad("ID_OLD")
    # Clean up with 0 days threshold shouldn't delete immediately unless time moves, but function call should work
    deleted = cleanup_old_ads(days=30)
    assert isinstance(deleted, int)
