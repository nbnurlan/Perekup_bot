import os
import unittest
import database

class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.test_db = "test_olx_ads.db"
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

    def test_filter_new_ads(self):
        database.save_ads(["ad1", "ad2", "ad3"])

        candidates = ["ad2", "ad3", "ad4", "ad5"]
        new_ads = database.filter_new_ads(candidates)

        self.assertEqual(new_ads, {"ad4", "ad5"})

    def test_filter_empty(self):
        self.assertEqual(database.filter_new_ads([]), set())

    def test_save_ads_batch(self):
        database.save_ads(["ad10", "ad11", "ad12"])
        self.assertFalse(database.is_new_ad("ad10"))
        self.assertFalse(database.is_new_ad("ad11"))
        self.assertFalse(database.is_new_ad("ad12"))

    def test_cleanup_old_ads(self):
        deleted = database.cleanup_old_ads(days=30)
        self.assertEqual(deleted, 0)

if __name__ == "__main__":
    unittest.main()
