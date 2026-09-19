import os
import tempfile
import unittest
import database

class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.temp_db.close()
        database.DB_PATH = self.temp_db.name
        database.init_db()

    def tearDown(self):
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)

    def test_single_ad_operations(self):
        self.assertTrue(database.is_new_ad("ad1"))
        database.save_ad("ad1")
        self.assertFalse(database.is_new_ad("ad1"))

    def test_batch_ad_operations(self):
        ad_ids = ["ad1", "ad2", "ad3"]

        # Initially none are seen
        seen = database.get_seen_ads(ad_ids)
        self.assertEqual(seen, set())

        # Save batch
        database.save_ads(["ad1", "ad3"])

        # Check batch seen
        seen = database.get_seen_ads(ad_ids)
        self.assertEqual(seen, {"ad1", "ad3"})

        self.assertFalse(database.is_new_ad("ad1"))
        self.assertTrue(database.is_new_ad("ad2"))
        self.assertFalse(database.is_new_ad("ad3"))

    def test_empty_batch_operations(self):
        self.assertEqual(database.get_seen_ads([]), set())
        database.save_ads([])  # should execute without error

if __name__ == "__main__":
    unittest.main()
