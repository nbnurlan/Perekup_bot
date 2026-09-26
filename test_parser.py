import pytest
from parser import _extract_ad_id, _parse_html, Ad


def test_extract_ad_id():
    url = "https://www.olx.kz/d/obyavlenie/iphone-13-pro-128gb-ID12345.html"
    assert _extract_ad_id(url) == "ID12345"

    url_no_id = "https://www.olx.kz/d/obyavlenie/some-title.html"
    assert _extract_ad_id(url_no_id) == "title"


def test_parse_html_with_cards():
    html_content = """
    <html>
      <body>
        <div data-cy="l-card">
          <a href="https://www.olx.kz/d/obyavlenie/test-ad-ID999.html">
            <h6 class="css-1w0343">Test Product</h6>
          </a>
          <p data-testid="ad-price">50 000 ₸</p>
          <p data-testid="location-date">Almaty, Today 10:00</p>
          <img src="https://img.olx.kz/photo1.jpg" />
        </div>
      </body>
    </html>
    """
    ads = _parse_html(html_content)
    assert len(ads) == 1
    ad = ads[0]
    assert ad.id == "ID999"
    assert ad.title == "Test Product"
    assert ad.price == "50 000 ₸"
    assert ad.location == "Almaty"
    assert ad.image == "https://img.olx.kz/photo1.jpg"


def test_parse_html_empty():
    assert _parse_html("<html><body></body></html>") == []
