from scrapers.base import ProductMatch, Scraper, extract_jsonld_products


class RealScraper(Scraper):
    name = "real"
    base_url = "https://www.realonline.com.py"
    search_path = "/busqueda?q={query}"  # robots.txt Content-Signal explicitly allows search/reference use

    def search(self, query: str) -> list[ProductMatch]:
        url = self.base_url + self.search_path.format(query=query)
        resp = self.session.get(url, timeout=10)
        resp.raise_for_status()
        products = extract_jsonld_products(resp.text)
        return [ProductMatch(p["name"], p["price"], resp.url) for p in products]
