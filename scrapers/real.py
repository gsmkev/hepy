from scrapers.base import ProductMatch, Scraper, extract_nextjs_rsc_products


class RealScraper(Scraper):
    name = "real"
    base_url = "https://www.realonline.com.py"
    # Confirmed live via browser network inspection: Real is a Next.js app
    # with no client-callable product-search API (the GraphQL backend at
    # nextgentheadless.instaleap.io only exposes autocomplete/tracking
    # operations to the browser). The search page's real product data comes
    # from the server-rendered RSC payload, requested by sending an
    # `RSC: 1` header — confirmed to work from plain requests, no headless
    # browser needed in production. robots.txt Content-Signal explicitly
    # allows search/reference use.
    search_path = "/search?name={query}"

    def search(self, query: str) -> list[ProductMatch]:
        url = self.base_url + self.search_path.format(query=query)
        resp = self.session.get(url, headers={"RSC": "1"}, timeout=10)
        resp.raise_for_status()
        products = extract_nextjs_rsc_products(resp.text)
        return [ProductMatch(p["name"], p["price"], resp.url) for p in products]
