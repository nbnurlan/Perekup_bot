## 2024-05-18 - BeautifulSoup HTML Parser Optimization
**Learning:** `lxml` is already included in `requirements.txt` and offers a ~35-40% execution speedup over Python's built-in `html.parser` when parsing OLX ad cards with BeautifulSoup4.
**Action:** Always prefer `lxml` parser backend for BeautifulSoup when `lxml` is available in project requirements.
