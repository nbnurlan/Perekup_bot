import os
import unittest
import sqlite3
import database

class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.test_db = "test_database.db"
        database.DB_PATH = self.test_db
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
        database.init_db()

    def tearDown(self):
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def test_single_ad_operations(self):
        self.assertTrue(database.is_new_ad("ad1"))
        database.save_ad("ad1")
        self.assertFalse(database.is_new_ad("ad1"))

    def test_batch_ad_operations(self):
        ad_ids = ["ad1", "ad2", "ad3", "ad4"]

        # All ads should be new initially
        new_ids = database.filter_new_ad_ids(ad_ids)
        self.assertEqual(new_ids, {"ad1", "ad2", "ad3", "ad4"})

        # Save a batch of ads
        database.save_ads_batch(["ad1", "ad2"])

        # Filter again
        new_ids_after = database.filter_new_ad_ids(ad_ids)
        self.assertEqual(new_ids_after, {"ad3", "ad4"})

        # Save remaining ads
        database.save_ads_batch(["ad3", "ad4"])
        self.assertEqual(database.filter_new_ad_ids(ad_ids), set())

    def test_empty_batch_operations(self):
        self.assertEqual(database.filter_new_ad_ids([]), set())
        # Should not raise any error
        database.save_ads_batch([])

    def test_cleanup_old_ads(self):
        # Insert an old ad manually
        with sqlite3.connect(self.test_db) as conn:
            conn.execute(
                "INSERT INTO seen_ads (ad_id, seen_at) VALUES (?, datetime('now', '-31 days'))",
                ("old_ad",)
            )
            conn.execute(
                "INSERT INTO seen_ads (ad_id, seen_at) VALUES (?, datetime('now', '-5 days'))",
                ("recent_ad",)
            )
            conn.commit()

        deleted = database.cleanup_old_ads(days=30)
        self.assertEqual(deleted, 1)
        self.assertFalse(database.is_new_ad("recent_ad"))
        self.assertTrue(database.is_new_ad("old_ad"))

if __name__ == "__main__":
    unittest.main()
