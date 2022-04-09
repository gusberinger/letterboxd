import unittest
from letterboxd_convert.database import DBConnection
from letterboxd_convert.download import download_urls


class DataBaseTest(unittest.TestCase):
    def test_singleton(self):
        db1 = DBConnection()
        db2 = DBConnection()
        self.assertEqual(db1, db2)

    def test_caching(self):
        db: DBConnection = DBConnection()
        db.clear_cache()
        self.assertRaises(
            KeyError,
            lambda: db.get_tconst("https://letterboxd.com/film/the-godfather/"),
        )
        _ = download_urls(["https://letterboxd.com/film/grey-gardens/"])
        self.assertEqual(
            "tt0073076", db.get_tconst("https://letterboxd.com/film/grey-gardens/")
        )


if __name__ == "__main__":
    unittest.main()
