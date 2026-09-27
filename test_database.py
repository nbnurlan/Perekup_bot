import os
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

import database


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.db_patcher = patch.object(database, "DB_PATH", self.db_path)
        self.db_patcher.start()
        database.init_db()

    def tearDown(self):
        self.db_patcher.stop()
        os.close(self.db_fd)
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def test_single_ad_operations(self):
        self.assertTrue(database.is_new_ad("ad1"))
        database.save_ad("ad1")
        self.assertFalse(database.is_new_ad("ad1"))

    def test_batch_get_existing_ad_ids(self):
        self.assertEqual(database.get_existing_ad_ids([]), set())
        self.assertEqual(
            database.get_existing_ad_ids(["ad1", "ad2"]), set()
        )

        database.save_ad("ad1")
        existing = database.get_existing_ad_ids(["ad1", "ad2", "ad3"])
        self.assertEqual(existing, {"ad1"})

    def test_batch_save_ads(self):
        database.save_ads([])
        database.save_ads(["ad10", "ad11", "ad12"])

        existing = database.get_existing_ad_ids(
            ["ad10", "ad11", "ad12", "ad13"]
        )
        self.assertEqual(existing, {"ad10", "ad11", "ad12"})

        # Test duplicate batch saving does not raise errors
        database.save_ads(["ad10", "ad14"])
        self.assertEqual(
            database.get_existing_ad_ids(["ad10", "ad14"]), {"ad10", "ad14"}
        )

    def test_chunking_large_batch(self):
        ad_ids = [f"ad_{i}" for i in range(1200)]
        database.save_ads(ad_ids)

        existing = database.get_existing_ad_ids(ad_ids)
        self.assertEqual(len(existing), 1200)

    def test_cleanup_old_ads(self):
        database.save_ads(["old1", "old2"])
        # Backdate old1 in database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE seen_ads SET seen_at = datetime('now', '-35 days') WHERE ad_id = 'old1'"
            )
            conn.commit()

        deleted = database.cleanup_old_ads(days=30)
        self.assertEqual(deleted, 1)
        self.assertFalse(database.is_new_ad("old2"))
        self.assertTrue(database.is_new_ad("old1"))


if __name__ == "__main__":
    unittest.main()
