import os
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

import database


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.temp_db.close()
        self.db_patcher = patch("database.DB_PATH", self.temp_db.name)
        self.db_patcher.start()
        database.init_db()

    def tearDown(self):
        self.db_patcher.stop()
        if os.path.exists(self.temp_db.name):
            os.remove(self.temp_db.name)

    def test_init_db(self):
        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='seen_ads'"
            )
            self.assertIsNotNone(cursor.fetchone())

    def test_is_new_ad_and_save_ad(self):
        ad_id = "test_ad_1"
        self.assertTrue(database.is_new_ad(ad_id))

        database.save_ad(ad_id)
        self.assertFalse(database.is_new_ad(ad_id))

    def test_filter_new_ad_ids_and_save_ads_batch(self):
        ad_ids = ["ad_10", "ad_11", "ad_12", "ad_13"]

        # Initially all should be new
        new_ids = database.filter_new_ad_ids(ad_ids)
        self.assertEqual(new_ids, set(ad_ids))

        # Save a subset via batch
        database.save_ads_batch(["ad_10", "ad_12"])

        # Filter should now return only remaining unsaved IDs
        remaining = database.filter_new_ad_ids(ad_ids)
        self.assertEqual(remaining, {"ad_11", "ad_13"})

        # Empty list check
        self.assertEqual(database.filter_new_ad_ids([]), set())

        # Save remaining
        database.save_ads_batch(["ad_11", "ad_13"])
        self.assertEqual(database.filter_new_ad_ids(ad_ids), set())

    def test_cleanup_old_ads(self):
        # Insert old record
        with sqlite3.connect(self.temp_db.name) as conn:
            conn.execute(
                "INSERT INTO seen_ads (ad_id, seen_at) VALUES (?, datetime('now', '-35 days'))",
                ("old_ad",),
            )
            conn.execute(
                "INSERT INTO seen_ads (ad_id, seen_at) VALUES (?, datetime('now'))",
                ("recent_ad",),
            )
            conn.commit()

        deleted = database.cleanup_old_ads(days=30)
        self.assertEqual(deleted, 1)

        self.assertFalse(database.is_new_ad("recent_ad"))
        self.assertTrue(database.is_new_ad("old_ad"))


if __name__ == "__main__":
    unittest.main()
