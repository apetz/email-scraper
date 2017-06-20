import unittest
from scrapy.http import Request, TextResponse
from scraper.spiders import thorough_spider


class SpiderTest(unittest.TestCase):

    def test_simple_parse(self):
        url = "http://test-url1.com"
        request = Request(url=url)
        file_content = open("html-test.html").read()
        response = TextResponse(url=url, request=request, body=file_content, encoding='utf-8')
        spider = thorough_spider.ThoroughSpider("test-url1.com")
        items = list(spider.parse(response))
        self.assertEqual(2, len(items), "Should have length = 2")
        self.assertEqual('bob@bob.com', (items[0]['email_address']), "should be bob@bob.com")

if __name__ == '__main__':
    unittest.main()