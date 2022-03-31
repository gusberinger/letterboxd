from turtle import down
import download
import unittest


class DownloadListTest(unittest.TestCase):
    

    def test_small_download(self):
        result = download.download_list("https://letterboxd.com/testuser_py/list/test-list/")
        self.assertEqual(list(result), ['tt0068646', 'tt6751668', 'tt8772262'])

    def test_favorites(self):
        result = download.download_list("https://letterboxd.com/testuser_py/likes/films/")
        self.assertEqual(list(result), ['tt0422720', 'tt0467406', 'tt0045152', 'tt3783958'])



if __name__ == '__main__':
    unittest.main()