import unittest
from unittest.mock import patch, MagicMock
from parser import _parse_html, fetch_ads, Ad


class TestParser(unittest.TestCase):
    def setUp(self):
        self.sample_html = """
        <!DOCTYPE html>
        <html>
        <body>
            <div data-cy="l-card" class="css-1sw3lx0">
                <a href="/d/obyavlenie/iphone-13-pro-ID12345.html">
                    <h6>iPhone 13 Pro 128GB</h6>
                    <p data-testid="ad-price">250 000 ₸</p>
                    <p data-testid="location-date">Almaty, Bostandyk, Bugun 12:30</p>
                    <img src="https://apollo-olx-c.akamaized.net/v1/files/sample/image;s=644x461" />
                </a>
            </div>
            <div data-cy="l-card" class="css-1sw3lx0">
                <a href="/d/obyavlenie/macbook-air-m1-ID67890.html">
                    <h6>MacBook Air M1</h6>
                    <p data-testid="ad-price">380 000 ₸</p>
                    <p data-testid="location-date">Astana, Today 14:00</p>
                </a>
            </div>
        </body>
        </html>
        """

    def test_parse_html_success(self):
        ads = _parse_html(self.sample_html)
        self.assertEqual(len(ads), 2)

        self.assertEqual(ads[0].id, "ID12345")
        self.assertEqual(ads[0].title, "iPhone 13 Pro 128GB")
        self.assertEqual(ads[0].price, "250 000 ₸")
        self.assertEqual(ads[0].location, "Almaty")
        self.assertEqual(ads[0].link, "https://www.olx.kz/d/obyavlenie/iphone-13-pro-ID12345.html")
        self.assertEqual(ads[0].image, "https://apollo-olx-c.akamaized.net/v1/files/sample/image;s=644x461")

        self.assertEqual(ads[1].id, "ID67890")
        self.assertEqual(ads[1].title, "MacBook Air M1")
        self.assertEqual(ads[1].price, "380 000 ₸")
        self.assertEqual(ads[1].location, "Astana")
        self.assertEqual(ads[1].link, "https://www.olx.kz/d/obyavlenie/macbook-air-m1-ID67890.html")
        self.assertIsNone(ads[1].image)

    def test_parse_html_empty(self):
        ads = _parse_html("<html><body><div>No cards here</div></body></html>")
        self.assertEqual(ads, [])

    @patch("parser.requests.get")
    def test_fetch_ads_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = self.sample_html
        mock_get.return_value = mock_response

        ads = fetch_ads("https://www.olx.kz/elektronika/")
        self.assertEqual(len(ads), 2)
        self.assertEqual(ads[0].id, "ID12345")

    @patch("parser.requests.get")
    def test_fetch_ads_http_error(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_get.return_value = mock_response

        ads = fetch_ads("https://www.olx.kz/elektronika/")
        self.assertEqual(ads, [])


if __name__ == "__main__":
    unittest.main()
