from turtle import down
import download
import unittest

small_list = ("https://letterboxd.com/testuser_py/list/test-list/", ['tt0068646', 'tt6751668', 'tt8772262'])
large_list = ("https://letterboxd.com/testuser_py/list/larger-list/", ['tt1232829', 'tt8579674', 'tt0068182', 'tt0080339', 'tt0103639', 'tt0870984', 'tt10260042', 'tt0103772', 'tt0120601', 'tt0052618', 'tt0040522', 'tt0118715', 'tt0265086', 'tt3480822', 'tt7349662', 'tt0090756', 'tt0080455', 'tt0088846', 'tt0388795', 'tt0103919', 'tt0074285', 'tt0162222', 'tt0071315', 'tt0082186', 'tt0100234', 'tt0088930', 'tt5073642', 'tt0091251', 'tt0327597', 'tt1650043', 'tt0097216', 'tt0918927', 'tt0363163', 'tt0780504', 'tt1160419', 'tt5013056', 'tt0080678', 'tt0082340', 'tt0070047', 'tt0061913', 'tt5083738', 'tt6053438', 'tt0800039', 'tt1341167', 'tt0067116', 'tt8847712', 'tt0217505', 'tt5052448', 'tt0162346', 'tt0060196', 'tt0099685', 'tt0058715', 'tt9243804', 'tt0107048', 'tt0113247', 'tt0056058', 'tt0110006', 'tt0064429', 'tt0076162', 'tt4698684', 'tt0118694', 'tt0816692', 'tt5104604', 'tt0418763', 'tt0073195', 'tt2911666', 'tt5715874', 'tt0085794', 'tt0085809', 'tt4925292', 'tt0816556', 'tt0095497', 'tt0104694', 'tt7984734', 'tt0120737', 'tt0167261', 'tt12801262', 'tt1235790', 'tt0049902', 'tt6998518', 'tt1615147', 'tt1560747', 'tt0209144', 'tt8772262', 'tt0117060', 'tt0120755', 'tt0317919', 'tt1229238', 'tt2381249', 'tt4912910', 'tt5569310', 'tt0120762', 'tt1308138', 'tt0166924', 'tt0145937', 'tt7914416', 'tt0156887', 'tt0084503', 'tt8613070', 'tt0095895', 'tt0414387', 'tt6644200', 'tt0081398', 'tt1899353', 'tt0040725', 'tt0105236', 'tt1663202', 'tt0267913', 'tt0117571', 'tt0114369', 'tt0050976', 'tt0015324', 'tt0167404', 'tt2948372', 'tt0079944', 'tt0076759', 'tt0086190', 'tt0120201', 'tt0053987', 'tt0838283', 'tt0028333', 'tt5700672', 'tt0841046', 'tt0063794', 'tt0059894', 'tt10370710', 'tt5311514', 'tt0054494', 'tt0115734', 'tt0432283'])
favorites = ("https://letterboxd.com/testuser_py/likes/films/", ['tt0422720', 'tt0467406', 'tt0045152', 'tt3783958'])

class DownloadListTest(unittest.TestCase):
    
    def test_small(self):
        url, ids = small_list
        result = download.download_list(url)
        self.assertEqual(list(result), ids)

    def test_large(self):
        url, ids = large_list
        result = download.download_list(url)
        self.assertEqual(list(result), ids)

    def test_favorites(self):
        url, ids = favorites
        result = download.download_list(url)
        self.assertEqual(list(result), ids)

    def test_small_limit(self):
        url, ids = small_list
        result = download.download_list(url, 3)
        self.assertEqual(list(result), ids[:3])

    def test_large_limit(self):
        url, ids = small_list
        result = download.download_list(url, 40)
        self.assertEqual(list(result), ids[:40])

    def test_args(self):
        
        self.assertEqual(
            download.parse_args("https://letterboxd.com/testuser_py/list/larger-list/ -limit 10"),
            {'url': 'https://letterboxd.com/testuser_py/list/larger-list/', 'limit': 10}
        )

        self.assertEqual(
            download.parse_args("https://letterboxd.com/testuser_py/list/larger-list/ -l 10"),
            {'url': 'https://letterboxd.com/testuser_py/list/larger-list/', 'limit': 10}
        )

        self.assertEqual(
            download.parse_args("https://letterboxd.com/testuser_py/list/larger-list/"),
            {'url': 'https://letterboxd.com/testuser_py/list/larger-list/', 'limit': None}
        )



if __name__ == '__main__':
    unittest.main()