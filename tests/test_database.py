import os
import pytest
import sqlite3
import database
from parser import Ad, _extract_ad_id, _parse_html

@pytest.fixture
def temp_db(tmp_path, monkeypatch):
    db_file = tmp_path / "test_olx.db"
    monkeypatch.setattr(database, "DB_PATH", str(db_file))
    database.init_db()
    return str(db_file)


def test_init_db(temp_db):
    assert os.path.exists(temp_db)
    with sqlite3.connect(temp_db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='seen_ads'")
        assert cursor.fetchone() is not None


def test_is_new_ad_and_save_ad(temp_db):
    ad_id = "test_ad_123"
    assert database.is_new_ad(ad_id) is True
    database.save_ad(ad_id)
    assert database.is_new_ad(ad_id) is False


def test_filter_new_ad_ids_and_save_ads(temp_db):
    ids = ["ad_1", "ad_2", "ad_3"]
    assert database.filter_new_ad_ids(ids) == {"ad_1", "ad_2", "ad_3"}

    database.save_ads(["ad_1", "ad_2"])

    assert database.filter_new_ad_ids(ids) == {"ad_3"}


def test_cleanup_old_ads(temp_db):
    with sqlite3.connect(temp_db) as conn:
        conn.execute(
            "INSERT INTO seen_ads (ad_id, seen_at) VALUES (?, datetime('now', '-35 days'))",
            ("old_ad_1",)
        )
        conn.execute(
            "INSERT INTO seen_ads (ad_id, seen_at) VALUES (?, datetime('now', '-5 days'))",
            ("recent_ad_1",)
        )
        conn.commit()

    deleted = database.cleanup_old_ads(days=30)
    assert deleted == 1
    assert database.is_new_ad("old_ad_1") is True
    assert database.is_new_ad("recent_ad_1") is False


def test_extract_ad_id():
    url = "https://www.olx.kz/d/obyavlenie/iphone-15-pro-max-ID12345.html"
    assert _extract_ad_id(url) == "ID12345"


def test_parse_html():
    sample_html = """
    <html>
      <body>
        <div data-cy="l-card">
          <a href="https://www.olx.kz/d/obyavlenie/test-phone-ID99999.html">
            <h6>Test Phone</h6>
          </a>
          <p data-testid="ad-price">100 000 ₸</p>
          <p data-testid="location-date">Almaty, Today 10:00</p>
          <img src="https://img.olx.kz/photo.jpg" />
        </div>
      </body>
    </html>
    """
    ads = _parse_html(sample_html)
    assert len(ads) == 1
    assert ads[0].id == "ID99999"
    assert ads[0].title == "Test Phone"
    assert ads[0].price == "100 000 ₸"
    assert ads[0].location == "Almaty"
    assert ads[0].image == "https://img.olx.kz/photo.jpg"
