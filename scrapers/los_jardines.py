from scrapers.base import ProductMatch, Scraper, extract_jsonld_products


class LosJardinesScraper(Scraper):
    name = "los_jardines"
    base_url = "https://www.losjardinesonline.com.py"
    search_path = "/busqueda?q={query}"  # ponytail: no robots.txt found; verify real search path against a live browser session before first production run

    def search(self, query: str) -> list[ProductMatch]:
        url = self.base_url + self.search_path.format(query=query)
        resp = self.session.get(url, timeout=10)
        resp.raise_for_status()
        products = extract_jsonld_products(resp.text)
        return [ProductMatch(p["name"], p["price"], resp.url) for p in products]
