from scrapers.base import ProductMatch, Scraper, extract_jsonld_products


class SuperseisScraper(Scraper):
    name = "superseis"
    base_url = "https://www.superseis.com.py"
    # ponytail: confirmed blocked even from a real (headless) browser session,
    # not just plain requests — CloudFront returns 403 before any page loads,
    # so this is a network/bot-fingerprint block, not a scraping-strategy
    # problem. No fix available without a non-datacenter residential network
    # or a stealth browser setup; run_daily.py's per-site error isolation
    # excludes it gracefully until that changes.
    search_path = "/busqueda?q={query}"

    def search(self, query: str) -> list[ProductMatch]:
        url = self.base_url + self.search_path.format(query=query)
        resp = self.session.get(url, timeout=10)
        resp.raise_for_status()
        products = extract_jsonld_products(resp.text)
        return [ProductMatch(p["name"], p["price"], resp.url) for p in products]
