from scrapers.base import ProductMatch, Scraper, extract_jsonld_products


class StockScraper(Scraper):
    name = "stock"
    base_url = "https://www.stock.com.py"
    search_path = "/search?q={query}"  # nopCommerce default search convention, confirmed not disallowed in robots.txt

    def search(self, query: str) -> list[ProductMatch]:
        url = self.base_url + self.search_path.format(query=query)
        resp = self.session.get(url, timeout=10)
        resp.raise_for_status()
        products = extract_jsonld_products(resp.text)
        return [ProductMatch(p["name"], p["price"], resp.url) for p in products]
