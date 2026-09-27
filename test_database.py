import os
import unittest
import sqlite3
import database
from database import (
    init_db,
    is_new_ad,
    save_ad,
    filter_new_ads,
    save_ads,
    cleanup_old_ads,
)

TEST_DB = "test_ads.db"


class TestDatabaseBatchOperations(unittest.TestCase):
    def setUp(self):
        database.DB_PATH = TEST_DB
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)
        init_db()

    def tearDown(self):
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)

    def test_filter_and_save_ads_batch(self):
        ad_ids = [f"ad_{i}" for i in range(10)]

        # Initially all ads should be new
        new_ads = filter_new_ads(ad_ids)
        self.assertEqual(new_ads, set(ad_ids))

        # Save half of the ads
        save_ads(ad_ids[:5])

        # Query again
        new_ads_after = filter_new_ads(ad_ids)
        self.assertEqual(new_ads_after, set(ad_ids[5:]))

    def test_single_ad_helpers(self):
        self.assertTrue(is_new_ad("single_ad_1"))
        save_ad("single_ad_1")
        self.assertFalse(is_new_ad("single_ad_1"))

    def test_empty_input(self):
        self.assertEqual(filter_new_ads([]), set())
        # Should not raise any error
        save_ads([])

    def test_chunking_large_inputs(self):
        large_ad_ids = [f"ad_large_{i}" for i in range(1200)]
        new_ads = filter_new_ads(large_ad_ids)
        self.assertEqual(len(new_ads), 1200)

        save_ads(large_ad_ids)
        new_ads_after = filter_new_ads(large_ad_ids)
        self.assertEqual(len(new_ads_after), 0)

    def test_cleanup_old_ads(self):
        save_ads(["old_ad_1", "old_ad_2"])
        # Backdate old_ad_1 to 35 days ago
        with sqlite3.connect(TEST_DB) as conn:
            conn.execute(
                "UPDATE seen_ads SET seen_at = datetime('now', '-35 days') WHERE ad_id = 'old_ad_1'"
            )
            conn.commit()

        deleted = cleanup_old_ads(days=30)
        self.assertEqual(deleted, 1)
        self.assertFalse(is_new_ad("old_ad_2"))
        self.assertTrue(is_new_ad("old_ad_1"))


if __name__ == "__main__":
    unittest.main()
