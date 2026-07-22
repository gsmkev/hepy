import db
import run_daily
from scrapers.base import ProductMatch, Scraper

BASKET = [
    {"product_key": "arroz", "nombre_canonico": "Arroz", "bcp_category": "cereales",
     "weight": 1.0, "queries": {"good": "arroz", "bad": "arroz"}},
]


class GoodScraper(Scraper):
    name = "good"

    def search(self, query):
        return [ProductMatch(name="Arroz", price=6500.0, url="https://good/p/1")]


class BadScraper(Scraper):
    name = "bad"

    def search(self, query):
        raise ConnectionError("site is down")


def test_run_daily_inserts_and_survives_one_site_failing(tmp_path):
    conn = db.connect(str(tmp_path / "t.db"))
    db.init_schema(conn)

    summary = run_daily.run(conn, BASKET, [GoodScraper(), BadScraper()], date="2026-07-22")

    assert summary["inserted"] == 1
    assert summary["failed_supermarkets"] == ["bad"]

    rows = db.read_prices(conn, product_key="arroz", supermarket="good")
    assert len(rows) == 1
    assert rows[0]["price"] == 6500.0


def test_export_json_csv_writes_csv_header_even_with_no_rows(tmp_path):
    conn = db.connect(str(tmp_path / "t.db"))
    db.init_schema(conn)
    csv_path = tmp_path / "prices.csv"
    json_path = tmp_path / "prices.json"
    index_path = tmp_path / "index.json"
    run_daily.export_json_csv(conn, str(json_path), str(csv_path), str(index_path))
    assert csv_path.exists()
    content = csv_path.read_text(encoding="utf-8")
    assert "date" in content  # header present
    assert content.count("\n") == 1  # header only, no data rows
