from scrapers.biggie import BiggieScraper


def test_search_parses_fixture(monkeypatch):
    scraper = BiggieScraper()
    with open("fixtures/biggie_search_arroz.html", encoding="utf-8") as f:
        fixture_html = f.read()

    class FakeResponse:
        text = fixture_html
        url = "https://www.biggie.com.py/buscar?q=arroz"
        def raise_for_status(self):
            pass

    monkeypatch.setattr(scraper.session, "get", lambda *a, **k: FakeResponse())
    results = scraper.search("arroz")
    assert len(results) == 1
    assert results[0].price == 6700.0
