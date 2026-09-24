import unittest
from bs4 import BeautifulSoup
from parser import _parse_html, Ad

class TestParser(unittest.TestCase):
    def test_parse_html(self):
        html_sample = '''
        <html><body>
        <div data-cy="l-card">
          <a href="/d/obyavlenie/iphone-13-ID123456.html">
            <h6>iPhone 13</h6>
            <p data-testid="ad-price">250 000 ₸</p>
            <p data-testid="location-date">Алматы, Медеуский - Сегодня в 10:00</p>
            <img src="https://example.com/img.jpg" />
          </a>
        </div>
        </body></html>
        '''
        ads = _parse_html(html_sample)
        self.assertEqual(len(ads), 1)
        self.assertEqual(ads[0].id, "ID123456")
        self.assertEqual(ads[0].title, "iPhone 13")
        self.assertEqual(ads[0].price, "250 000 ₸")
        self.assertEqual(ads[0].location, "Алматы")
        self.assertEqual(ads[0].link, "https://www.olx.kz/d/obyavlenie/iphone-13-ID123456.html")
        self.assertEqual(ads[0].image, "https://example.com/img.jpg")

if __name__ == "__main__":
    unittest.main()
