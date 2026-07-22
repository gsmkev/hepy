from scrapers.los_jardines import LosJardinesScraper


def test_search_parses_fixture(monkeypatch):
    scraper = LosJardinesScraper()
    with open("fixtures/los_jardines_search_arroz.html", encoding="utf-8") as f:
        fixture_html = f.read()

    class FakeResponse:
        text = fixture_html
        url = "https://www.losjardinesonline.com.py/busqueda?q=arroz"
        def raise_for_status(self):
            pass

    monkeypatch.setattr(scraper.session, "get", lambda *a, **k: FakeResponse())
    results = scraper.search("arroz")
    assert len(results) == 1
    assert results[0].price == 6350.0
