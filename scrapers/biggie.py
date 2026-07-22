from scrapers.base import ProductMatch, Scraper, extract_jsonld_products


class BiggieScraper(Scraper):
    name = "biggie"
    base_url = "https://www.biggie.com.py"
    search_path = "/buscar?q={query}"  # ponytail: site is a Next.js SPA — confirm SSR includes JSON-LD, else switch to its internal JSON API before trusting in production

    def search(self, query: str) -> list[ProductMatch]:
        url = self.base_url + self.search_path.format(query=query)
        resp = self.session.get(url, timeout=10)
        resp.raise_for_status()
        products = extract_jsonld_products(resp.text)
        return [ProductMatch(p["name"], p["price"], resp.url) for p in products]
