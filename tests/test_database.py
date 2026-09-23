import unittest
import os
import sqlite3
import tempfile
import database
import config

class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        config.DB_PATH = self.db_path
        database.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='seen_ads'")
            self.assertIsNotNone(cursor.fetchone())

    def test_is_new_ad_and_save_ad(self):
        self.assertTrue(database.is_new_ad("ad123"))
        database.save_ad("ad123")
        self.assertFalse(database.is_new_ad("ad123"))

    def test_save_ads_batch(self):
        ads = ["ad101", "ad102", "ad103"]
        for ad_id in ads:
            self.assertTrue(database.is_new_ad(ad_id))
        database.save_ads_batch(ads)
        for ad_id in ads:
            self.assertFalse(database.is_new_ad(ad_id))

    def test_filter_new_ads(self):
        database.save_ad("ad_old")
        candidates = ["ad_old", "ad_new1", "ad_new2"]
        new_ads = database.filter_new_ads(candidates)
        self.assertEqual(new_ads, ["ad_new1", "ad_new2"])

    def test_cleanup_old_ads(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO seen_ads (ad_id, seen_at) VALUES ('old', datetime('now', '-35 days'))"
            )
            conn.execute(
                "INSERT INTO seen_ads (ad_id, seen_at) VALUES ('recent', datetime('now', '-5 days'))"
            )
            conn.commit()

        deleted = database.cleanup_old_ads(days=30)
        self.assertEqual(deleted, 1)
        self.assertFalse(database.is_new_ad("recent"))
        self.assertTrue(database.is_new_ad("old"))

if __name__ == '__main__':
    unittest.main()
