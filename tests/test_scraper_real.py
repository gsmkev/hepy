from scrapers.real import RealScraper


def test_search_parses_fixture(monkeypatch):
    scraper = RealScraper()
    with open("fixtures/real_search_arroz.txt", encoding="utf-8") as f:
        fixture_text = f.read()

    class FakeResponse:
        text = fixture_text
        url = "https://www.realonline.com.py/search?name=arroz"
        def raise_for_status(self):
            pass

    captured_headers = {}

    def fake_get(*a, **k):
        captured_headers.update(k.get("headers", {}))
        return FakeResponse()

    monkeypatch.setattr(scraper.session, "get", fake_get)
    results = scraper.search("arroz")
    assert len(results) == 2
    assert results[0].name == "Arroz Primicia Amarillo, 500grs"
    assert results[0].price == 3550.0
    assert results[1].name == "Arroz Primicia rojo, 500gr"
    assert results[1].price == 13800.0
    assert captured_headers.get("RSC") == "1"
