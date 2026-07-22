from scrapers.base import ProductMatch, Scraper, extract_jsonld_products


class GrutterScraper(Scraper):
    name = "grutter"
    base_url = "https://grutteronline.casagrutter.com.py"
    search_path = "/busqueda?q={query}"  # ponytail: domain was unreachable from the planning sandbox; confirm reachability from the real execution environment first

    def search(self, query: str) -> list[ProductMatch]:
        url = self.base_url + self.search_path.format(query=query)
        resp = self.session.get(url, timeout=10)
        resp.raise_for_status()
        products = extract_jsonld_products(resp.text)
        return [ProductMatch(p["name"], p["price"], resp.url) for p in products]
