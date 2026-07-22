## Hepy — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and ship the first running version of Hepy — a daily-updating, weighted price index for Paraguay built by scraping 9 online supermarkets, validated against the official BCP IPC, published as an open dataset (CC-BY) + open code (Apache-2.0), with a static dashboard deployable to Cloudflare Pages and the data-collection scaffolding for a future ML nowcasting phase.

**Architecture:** A Python package with one scraper module per supermarket behind a shared interface, a SQLite database as the single source of truth, a pure-function index/outlier layer that never touches the network, a daily orchestrator script triggered by GitHub Actions, and a static HTML/JS dashboard (Chart.js) that fetches the release-published `index.json` client-side — no server, deployable to Cloudflare Pages as static files. Reference: design doc `2026-07-22-hepy-indice-precios-design` (Outline, collection "Superpowers"); revised after initial planning to drop Streamlit in favor of a Cloudflare-Pages-compatible static site (see Task 21 revision note).

**Tech Stack:** Python 3.11+, `requests`, `beautifulsoup4`, stdlib `sqlite3`/`statistics`/`json` for the backend; plain HTML/JS + Chart.js (CDN, SRI-pinned) for the dashboard — no frontend build tooling, no framework. No `pandas`/`numpy`/ML libraries in this plan — they are intentionally deferred to when Phase 2 (nowcasting) is actually implemented, per YAGNI.

## Global Constraints

* Code license: Apache-2.0. Data license: CC-BY (attribution required). Both files must exist at repo root before any data is published.
* Working name for the project/index everywhere in code, repo, and UI: **Hepy**.
* No new dependency may be added if the stdlib already covers the need (ponytail rule) — this governs `index.py` (use `statistics.geometric_mean` / manual math, not `numpy`) and `outliers.py` (use `statistics.median`, not `scipy`).
* Every scraper must go through the JSON-LD-first strategy in `scrapers/base.py` before any site-specific CSS parsing is written (Task 5) — this is a project-wide convention, not a per-task choice.
* Every non-trivial module (parsers, `index.py`, `outliers.py`) ships with a fixture- or toy-data-based test — no module is "done" without its test passing.
* `prices.db` and any other data artifact are never committed to git — they live only in the GitHub Release `dataset` (per design doc). `.gitignore` must exclude `*.db`, `*.csv`, `*.json` data exports from day one (Task 1).


---

## Known facts gathered during planning (do not re-derive)

Real reconnaissance was done from the planning sandbox before writing this plan — reuse these findings instead of re-fetching from scratch, though re-verification from a real network is still required where noted:

| Supermarket | Domain | robots.txt | Notes |
|-------------|--------|------------|-------|
| Superseis   | `www.superseis.com.py` | **Blocked** — CloudFront returns HTTP 403 to `robots.txt` itself | Aggressive bot protection at the CDN layer. May need a different network/IP or may simply not be scrapable with plain `requests`. Flag in legal review; do not assume it's off-limits until re-tested from a real (non-datacenter) network — CloudFront often blocks datacenter IP ranges specifically. |
| Stock       | `www.stock.com.py` | HTTP 200, standard **nopCommerce** default disallow list (checkout/account/payment paths) | No disallow on `/search`. Runs nopCommerce (.NET) — its search endpoint convention is `/search?q=<term>`. |
| Casa Rica   | `www.casarica.com.py` | HTTP 404 (no robots.txt file) | Absence of a file is conventionally permissive, but still check ToS manually per Task 3. |
| Salemma     | `www.salemmaonline.com.py` | HTTP 200, disallows `/carrito`, `/checkout`, `/cuenta`, `/login`, etc.; explicitly `Allow: *?page=1/2` | Product/category browsing is not disallowed. |
| Biggie      | `www.biggie.com.py` (redirects, canonical `biggie.com.py`) | Not yet fetched (redirect) | Frontend is **Next.js** (a JS SPA) — plain `requests` will likely only get an app shell. Check for a JSON API (`/_next/data/...` or an internal REST endpoint) before assuming JSON-LD/HTML scraping works. |
| Areté       | `www.arete.com.py` | HTTP 404 (no robots.txt file) | Check ToS manually. |
| Grütter     | `grutteronline.casagrutter.com.py` | **Unreachable from this sandbox** (connection failure, not a 403/404) | Retry from the implementation environment; may be a transient/DNS issue specific to this sandbox. |
| Los Jardines | `www.losjardinesonline.com.py` | HTTP 404 (no robots.txt file) | Check ToS manually. |
| Real        | `www.realonline.com.py` | HTTP 200, uses the **Content-Signal** directive: `Content-Signal: search=yes,ai-train=no,use=reference` | Explicitly permits "search" (indexing) and "reference" use, explicitly forbids AI-training use. Hepy's use (price reference dataset, not model training on their content) fits `use=reference` cleanly — cite this explicitly in the paper/README as evidence of good-faith compliance. |

BCP IPC methodology source (for Task 4): "Recuadro II: Metodología de cálculo del Índice de Precios al Consumidor en Paraguay", `https://www.bcp.gov.py/documents/20117/79988/Recuadro+II_Metodologia+del+Calculo+de+Indices+de+Precios+al+Consumidor+en+Paraguay.pdf`. The IPC canasta is based on the 2015-2016 Encuesta de Presupuesto Familiar (EPF), 167 products, base December 2017, covering food, hygiene, household cleaning, and alcoholic/non-alcoholic beverages among other divisions.


---

### Task 1: Project scaffolding & licenses

**Files:**

* Create: `pyproject.toml`
* Create: `requirements.txt`
* Create: `.gitignore`
* Create: `LICENSE-CODE`
* Create: `LICENSE-DATA`
* Create: `README.md`

**Interfaces:**

```
requests>=2.31
beautifulsoup4>=4.12
streamlit>=1.38
pytest>=8.0
```

- [ ] **Step 2: Create** `**.gitignore**`

```
__pycache__/
*.pyc
.venv/
*.db
*.csv
*.json
!basket.json
!package.json
.streamlit/
```

- [ ] **Step 3: Create** `**pyproject.toml**`

```toml
[project]
name = "hepy"
version = "0.1.0"
description = "Hepy — índice de precios de alta frecuencia para Paraguay, validado contra el IPC-BCP"
requires-python = ">=3.11"

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 4: Create** `**LICENSE-CODE**`

Fetch the standard Apache License 2.0 text and save it verbatim to `LICENSE-CODE` (use `curl https://www.apache.org/licenses/LICENSE-2.0.txt -o LICENSE-CODE` or copy from a known-good local template — do not paraphrase the license text).

- [ ] **Step 5: Create** `**LICENSE-DATA**`

```
Hepy Dataset License: CC BY 4.0

The data files distributed with this project (prices.db, prices.csv, prices.json, index.json,
and any other exports under the "dataset" GitHub Release) are licensed under the
Creative Commons Attribution 4.0 International License (CC BY 4.0).

https://creativecommons.org/licenses/by/4.0/

Attribution: cite as "Hepy — Koeti Labs (<year>), <dataset URL>".
```

- [ ] **Step 6: Create** `**README.md**` **skeleton**

```markdown
## Hepy

Índice de precios de alta frecuencia para Paraguay, construido con scraping diario
de 9 supermercados online, ponderado con la metodología del IPC del Banco Central
del Paraguay (BCP), y validado empíricamente contra la serie oficial.

- Código: Apache-2.0 (`LICENSE-CODE`)
- Dataset: CC BY 4.0 (`LICENSE-DATA`) — citar como "Hepy — Koeti Labs (<año>), <URL del dataset>"
- Dataset descargable: ver la sección "Releases" del repo (`prices.db`, `prices.csv`, `prices.json`, `index.json`)

### Desarrollo

    pip install -r requirements.txt
    pytest
```

- [ ] **Step 7: Verify the environment installs cleanly**

Run: `python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt` Expected: no errors, all 4 packages install.

- [ ] **Step 8: Commit**

```bash
git init
git add pyproject.toml requirements.txt .gitignore LICENSE-CODE LICENSE-DATA README.md
git commit -m "chore: project scaffolding, licenses (Apache-2.0 code / CC BY 4.0 data)"
```


---

### Task 2: SQLite schema (`db.py`)

**Files:**

* Create: `db.py`
* Test: `tests/test_db.py`

**Interfaces:**

```python
# tests/test_db.py
import sqlite3
import db

def test_insert_and_read_price(tmp_path):
    conn = db.connect(str(tmp_path / "test.db"))
    db.init_schema(conn)
    db.insert_price(conn, "2026-07-22", "stock", "arroz_1kg", "Arroz 1kg", 6500.0, "https://stock.com.py/p/1")
    rows = db.read_prices(conn, product_key="arroz_1kg")
    assert len(rows) == 1
    assert rows[0]["supermarket"] == "stock"
    assert rows[0]["price"] == 6500.0
    assert rows[0]["is_outlier"] == 0

def test_index_daily_roundtrip(tmp_path):
    conn = db.connect(str(tmp_path / "test.db"))
    db.init_schema(conn)
    db.write_index_daily(conn, "2026-07-22", "AGREGADO", 100.0)
    db.write_index_daily(conn, "2026-07-23", "AGREGADO", 101.2)
    rows = db.read_index_daily(conn, supermarket="AGREGADO")
    assert [r["value"] for r in rows] == [100.0, 101.2]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_db.py -v` Expected: FAIL with `ModuleNotFoundError: No module named 'db'`

- [ ] **Step 3: Write the implementation**

```python
# db.py
import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    supermarket TEXT NOT NULL,
    product_key TEXT NOT NULL,
    product_name TEXT NOT NULL,
    price REAL NOT NULL,
    url TEXT NOT NULL,
    is_outlier INTEGER NOT NULL DEFAULT 0,
    UNIQUE(date, supermarket, product_key)
);

CREATE TABLE IF NOT EXISTS index_daily (
    date TEXT NOT NULL,
    supermarket TEXT NOT NULL,
    value REAL NOT NULL,
    UNIQUE(date, supermarket)
);
"""


def connect(path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    conn.commit()


def insert_price(
    conn: sqlite3.Connection,
    date: str,
    supermarket: str,
    product_key: str,
    product_name: str,
    price: float,
    url: str,
    is_outlier: bool = False,
) -> None:
    conn.execute(
        """INSERT OR REPLACE INTO prices
           (date, supermarket, product_key, product_name, price, url, is_outlier)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (date, supermarket, product_key, product_name, price, url, int(is_outlier)),
    )
    conn.commit()


def read_prices(
    conn: sqlite3.Connection,
    product_key: str | None = None,
    supermarket: str | None = None,
) -> list[dict]:
    query = "SELECT * FROM prices WHERE 1=1"
    params: list[str] = []
    if product_key is not None:
        query += " AND product_key = ?"
        params.append(product_key)
    if supermarket is not None:
        query += " AND supermarket = ?"
        params.append(supermarket)
    query += " ORDER BY date ASC"
    return [dict(row) for row in conn.execute(query, params)]


def write_index_daily(conn: sqlite3.Connection, date: str, supermarket: str, value: float) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO index_daily (date, supermarket, value) VALUES (?, ?, ?)",
        (date, supermarket, value),
    )
    conn.commit()


def read_index_daily(conn: sqlite3.Connection, supermarket: str | None = None) -> list[dict]:
    query = "SELECT * FROM index_daily"
    params: list[str] = []
    if supermarket is not None:
        query += " WHERE supermarket = ?"
        params.append(supermarket)
    query += " ORDER BY date ASC"
    return [dict(row) for row in conn.execute(query, params)]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_db.py -v` Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add db.py tests/test_db.py
git commit -m "feat: SQLite schema for prices and daily index"
```


---

### Task 3: Legal / ToS review (`legal/revision_tos.md`)

**Files:**

* Create: `legal/revision_tos.md`

**Interfaces:**

```markdown
# Revisión de ToS / robots.txt — Hepy

| Sitio | robots.txt | Términos de Servicio | Rate limit aplicado | Decisión |
|---|---|---|---|---|
| Superseis (superseis.com.py) | Bloqueado por CloudFront incluso para /robots.txt (403) | Pendiente de revisión manual (no se pudo cargar la página) | N/A hasta poder acceder | **Reintentar desde red no-datacenter antes de implementar el scraper.** Si sigue bloqueado, documentar como no-viable para v1 y excluir de la canasta agregada (afecta solo cobertura, no invalida el resto). |
| Stock (stock.com.py) | HTTP 200, disallow estándar de nopCommerce (checkout/cuenta/pagos), sin disallow sobre /search | Revisar ToS del sitio manualmente antes de la Task 7 | 1 request cada 2-3s, User-Agent identificado con contacto | Permitido |
| Casa Rica (casarica.com.py) | Sin archivo robots.txt (404) | Revisar ToS manualmente antes de la Task 8 | 1 request cada 2-3s | Permitido, sujeto a revisión de ToS |
| Salemma (salemmaonline.com.py) | HTTP 200, disallow de carrito/checkout/cuenta/login; permite `?page=` | Revisar ToS manualmente antes de la Task 9 | 1 request cada 2-3s | Permitido |
| Biggie (biggie.com.py) | Redirect, no confirmado aún | Revisar ToS manualmente antes de la Task 10; sitio es un SPA Next.js, verificar si expone una API JSON interna antes de scrapear HTML | 1 request cada 2-3s | Permitido con reserva técnica (puede requerir usar su API en vez de HTML) |
| Areté (arete.com.py) | Sin archivo robots.txt (404) | Revisar ToS manualmente antes de la Task 11 | 1 request cada 2-3s | Permitido, sujeto a revisión de ToS |
| Grütter (grutteronline.casagrutter.com.py) | Inalcanzable desde el sandbox de planificación (fallo de conexión, no 403/404) | Reintentar conexión y revisar ToS antes de la Task 12 | 1 request cada 2-3s | Pendiente de confirmar accesibilidad |
| Los Jardines (losjardinesonline.com.py) | Sin archivo robots.txt (404) | Revisar ToS manualmente antes de la Task 13 | 1 request cada 2-3s | Permitido, sujeto a revisión de ToS |
| Real (realonline.com.py) | HTTP 200, declara `Content-Signal: search=yes,ai-train=no,use=reference` | Revisar ToS manualmente antes de la Task 14 | 1 request cada 2-3s | **Permitido explícitamente para "reference"** — citar este directive en el paper/README como evidencia de buena fe |

Regla general aplicada a los 9 scrapers: identificarse con un User-Agent propio
(`Hepy/0.1 (+https://github.com/<org>/hepy; contacto: <email>)`), 1 request cada
2-3 segundos por sitio, nunca en paralelo entre sitios distintos en la misma
ventana de tiempo, y respetar cualquier `Disallow` de robots.txt aunque el
scraping general esté permitido.
```

- [ ] **Step 2: Commit**

```bash
git add legal/revision_tos.md
git commit -m "docs: legal/ToS reconnaissance for the 9 target supermarkets"
```


---

### Task 4: Canasta IPC-BCP (`basket.json`)

**Files:**

* Create: `basket.json`
* Test: `tests/test_basket.py`

**Interfaces:**

```python
# tests/test_basket.py
import json

def test_basket_weights_sum_to_one():
    with open("basket.json", encoding="utf-8") as f:
        basket = json.load(f)
    total = sum(item["weight"] for item in basket)
    assert abs(total - 1.0) < 1e-6

def test_basket_items_have_required_fields():
    with open("basket.json", encoding="utf-8") as f:
        basket = json.load(f)
    assert len(basket) >= 20
    for item in basket:
        assert item["product_key"]
        assert item["nombre_canonico"]
        assert item["bcp_category"]
        assert 0 < item["weight"] < 1
        assert isinstance(item["queries"], dict)
        assert len(item["queries"]) == 9  # one search query per supermarket
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_basket.py -v` Expected: FAIL with `FileNotFoundError: basket.json`

- [ ] **Step 3: Author** `**basket.json**`

Source the category structure and weights from the BCP methodology document ("Recuadro II: Metodología de cálculo del Índice de Precios al Consumidor en Paraguay", `https://www.bcp.gov.py/documents/20117/79988/...`) — read the divisions and their relative weights (base December 2017, EPF 2015-2016), pick the \~25-30 most weighted *food and household* items within reach of the 9 supermarkets (canasta chica, not the full 167-product IPC canasta), and normalize their weights to sum to 1.0 within this reduced sub-basket. Fill in each supermarket's exact search term for the product (verified once each scraper task fetches real search results — placeholder query strings here are acceptable at this stage and get corrected in Tasks 6-14 as each site is inspected).

Example shape (extend to the full \~25-30 items):

```json
[
  {
    "product_key": "arroz_1kg",
    "nombre_canonico": "Arroz blanco 1kg",
    "bcp_category": "alimentos_cereales",
    "weight": 0.06,
    "queries": {
      "superseis": "arroz 1kg",
      "stock": "arroz 1kg",
      "casa_rica": "arroz 1kg",
      "salemma": "arroz 1kg",
      "biggie": "arroz 1kg",
      "arete": "arroz 1kg",
      "grutter": "arroz 1kg",
      "los_jardines": "arroz 1kg",
      "real": "arroz 1kg"
    }
  }
]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_basket.py -v` Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add basket.json tests/test_basket.py
git commit -m "feat: canasta básica reducida basada en categorías y pesos del IPC-BCP"
```


---

### Task 5: Scraper interface & JSON-LD helper (`scrapers/base.py`)

**Files:**

* Create: `scrapers/__init__.py` (empty)
* Create: `scrapers/base.py`
* Test: `tests/test_scrapers_base.py`
* Create: `fixtures/jsonld_sample.html`

**Interfaces:**

* Produces: `ProductMatch` (dataclass: `name: str`, `price: float`, `url: str`), `extract_jsonld_products(html: str) -> list[dict]`, `Scraper` (base class: attributes `name: str`, `base_url: str`; method `search(self, query: str) -> list[ProductMatch]`, raises `NotImplementedError` in the base).
* Consumed by: every `scrapers/<site>.py` in Tasks 6-14.

**Why JSON-LD first:** most Paraguayan e-commerce sites (VTEX, WooCommerce, Tiendanube, nopCommerce) embed `schema.org/Product` structured data in `<script type="application/ld+json">` tags for SEO. Parsing that is far more robust than guessing CSS class names, and it's the same code across sites — only the URL/query pattern differs per site.

- [ ] **Step 1: Create the fixture**

```html
<!-- fixtures/jsonld_sample.html -->
<html><head>
<script type="application/ld+json">
{"@context": "https://schema.org", "@type": "Product", "name": "Arroz Blanco 1kg",
 "offers": {"@type": "Offer", "price": "6500", "priceCurrency": "PYG"}}
</script>
<script type="application/ld+json">
[{"@context": "https://schema.org", "@type": "Product", "name": "Aceite de Girasol 900ml",
  "offers": [{"@type": "Offer", "price": "12900", "priceCurrency": "PYG"}]}]
</script>
<script type="application/ld+json">not valid json</script>
</head><body></body></html>
```

- [ ] **Step 2: Write the failing test**

```python
# tests/test_scrapers_base.py
from scrapers.base import extract_jsonld_products, Scraper, ProductMatch

def test_extract_jsonld_products_from_fixture():
    with open("fixtures/jsonld_sample.html", encoding="utf-8") as f:
        html = f.read()
    products = extract_jsonld_products(html)
    assert len(products) == 2
    assert products[0] == {"name": "Arroz Blanco 1kg", "price": 6500.0}
    assert products[1] == {"name": "Aceite de Girasol 900ml", "price": 12900.0}

def test_scraper_base_search_not_implemented():
    scraper = Scraper()
    try:
        scraper.search("arroz")
        assert False, "expected NotImplementedError"
    except NotImplementedError:
        pass

def test_product_match_dataclass():
    p = ProductMatch(name="Arroz 1kg", price=6500.0, url="https://x.com/p/1")
    assert p.name == "Arroz 1kg"
    assert p.price == 6500.0
```

- [ ] **Step 3: Run test to verify it fails**

Run: `pytest tests/test_scrapers_base.py -v` Expected: FAIL with `ModuleNotFoundError: No module named 'scrapers'`

- [ ] **Step 4: Write the implementation**

```python
# scrapers/base.py
import json
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup

USER_AGENT = "Hepy/0.1 (+https://github.com/koeti-labs/hepy; contacto: labs@koeti.dev)"


@dataclass
class ProductMatch:
    name: str
    price: float
    url: str


def extract_jsonld_products(html: str) -> list[dict]:
    """Parse schema.org Product JSON-LD blocks embedded in a page.

    Returns a list of {"name": str, "price": float}. Malformed or non-Product
    blocks are skipped silently, never raise.
    """
    soup = BeautifulSoup(html, "html.parser")
    products: list[dict] = []
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(tag.string or "")
        except (json.JSONDecodeError, TypeError):
            continue
        items = data if isinstance(data, list) else [data]
        for item in items:
            if not isinstance(item, dict) or item.get("@type") != "Product":
                continue
            offers = item.get("offers", {})
            if isinstance(offers, list):
                offers = offers[0] if offers else {}
            name = item.get("name")
            price = offers.get("price") if isinstance(offers, dict) else None
            if name and price is not None:
                try:
                    products.append({"name": name, "price": float(price)})
                except (TypeError, ValueError):
                    continue
    return products


class Scraper:
    name: str = "base"
    base_url: str = ""

    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers["User-Agent"] = USER_AGENT

    def search(self, query: str) -> list[ProductMatch]:
        raise NotImplementedError
```

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/test_scrapers_base.py -v` Expected: PASS (3 tests)

- [ ] **Step 6: Commit**

```bash
git add scrapers/__init__.py scrapers/base.py tests/test_scrapers_base.py fixtures/jsonld_sample.html
git commit -m "feat: scraper base interface with JSON-LD product extraction"
```


---

### Task 6: Superseis scraper (reference implementation)

**Files:**

* Create: `scrapers/superseis.py`
* Test: `tests/test_scraper_superseis.py`
* Create: `fixtures/superseis_search_arroz.html`

**Interfaces:**

* Consumes: `scrapers.base.Scraper`, `scrapers.base.extract_jsonld_products`, `scrapers.base.ProductMatch`.
* Produces: `SuperseisScraper` (subclass of `Scraper`, `name = "superseis"`).

**Known constraint (from Task 3):** this site returned HTTP 403 from CloudFront even for `robots.txt` during planning. Implement the scraper exactly like the others (same JSON-LD strategy), but the test in this task runs only against the saved fixture — it does not require live network access. Before this scraper is trusted in production (`run_daily.py`, Task 17), re-run it manually against the live site from the real execution environment (not the planning sandbox) and confirm it isn't blocked; if still blocked, mark it excluded in `legal/revision_tos.md` and let `run_daily.py`'s per-site error handling (Task 17) skip it gracefully.

- [ ] **Step 1: Create the fixture**

```html
<!-- fixtures/superseis_search_arroz.html -->
<html><head>
<script type="application/ld+json">
{"@context": "https://schema.org", "@type": "Product", "name": "Arroz Blanco 1kg Superseis",
 "offers": {"@type": "Offer", "price": "6450", "priceCurrency": "PYG"}}
</script>
</head><body></body></html>
```

- [ ] **Step 2: Write the failing test**

```python
# tests/test_scraper_superseis.py
from scrapers.superseis import SuperseisScraper

def test_search_parses_fixture(monkeypatch):
    scraper = SuperseisScraper()

    with open("fixtures/superseis_search_arroz.html", encoding="utf-8") as f:
        fixture_html = f.read()

    class FakeResponse:
        text = fixture_html
        url = "https://www.superseis.com.py/busqueda?q=arroz"
        def raise_for_status(self):
            pass

    monkeypatch.setattr(scraper.session, "get", lambda *a, **k: FakeResponse())

    results = scraper.search("arroz")
    assert len(results) == 1
    assert results[0].name == "Arroz Blanco 1kg Superseis"
    assert results[0].price == 6450.0
```

- [ ] **Step 3: Run test to verify it fails**

Run: `pytest tests/test_scraper_superseis.py -v` Expected: FAIL with `ModuleNotFoundError: No module named 'scrapers.superseis'`

- [ ] **Step 4: Write the implementation**

```python
# scrapers/superseis.py
from scrapers.base import ProductMatch, Scraper, extract_jsonld_products


class SuperseisScraper(Scraper):
    name = "superseis"
    base_url = "https://www.superseis.com.py"
    search_path = "/busqueda?q={query}"  # ponytail: verify against a live browser session — site blocked automated fetches (CloudFront 403) during planning

    def search(self, query: str) -> list[ProductMatch]:
        url = self.base_url + self.search_path.format(query=query)
        resp = self.session.get(url, timeout=10)
        resp.raise_for_status()
        products = extract_jsonld_products(resp.text)
        return [ProductMatch(p["name"], p["price"], resp.url) for p in products]
```

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/test_scraper_superseis.py -v` Expected: PASS (1 test)

- [ ] **Step 6: Commit**

```bash
git add scrapers/superseis.py tests/test_scraper_superseis.py fixtures/superseis_search_arroz.html
git commit -m "feat: Superseis scraper (JSON-LD strategy)"
```


---

### Task 7: Stock scraper

**Files:**

* Create: `scrapers/stock.py`
* Test: `tests/test_scraper_stock.py`
* Create: `fixtures/stock_search_arroz.html`

**Interfaces:**

* Consumes: same as Task 6.
* Produces: `StockScraper` (`name = "stock"`).

**Known constraint (from Task 3):** confirmed nopCommerce platform, robots.txt reachable and does not disallow `/search`. nopCommerce's conventional search path is `/search?q=<term>`.

- [ ] **Step 1: Create the fixture**

```html
<!-- fixtures/stock_search_arroz.html -->
<html><head>
<script type="application/ld+json">
{"@context": "https://schema.org", "@type": "Product", "name": "Arroz Blanco 1kg Stock",
 "offers": {"@type": "Offer", "price": "6300", "priceCurrency": "PYG"}}
</script>
</head><body></body></html>
```

- [ ] **Step 2: Write the failing test**

```python
# tests/test_scraper_stock.py
from scrapers.stock import StockScraper

def test_search_parses_fixture(monkeypatch):
    scraper = StockScraper()
    with open("fixtures/stock_search_arroz.html", encoding="utf-8") as f:
        fixture_html = f.read()

    class FakeResponse:
        text = fixture_html
        url = "https://www.stock.com.py/search?q=arroz"
        def raise_for_status(self):
            pass

    monkeypatch.setattr(scraper.session, "get", lambda *a, **k: FakeResponse())
    results = scraper.search("arroz")
    assert len(results) == 1
    assert results[0].price == 6300.0
```

- [ ] **Step 3: Run test to verify it fails**

Run: `pytest tests/test_scraper_stock.py -v` Expected: FAIL with `ModuleNotFoundError: No module named 'scrapers.stock'`

- [ ] **Step 4: Write the implementation**

```python
# scrapers/stock.py
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
```

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/test_scraper_stock.py -v` Expected: PASS (1 test)

- [ ] **Step 6: Commit**

```bash
git add scrapers/stock.py tests/test_scraper_stock.py fixtures/stock_search_arroz.html
git commit -m "feat: Stock scraper (JSON-LD strategy, nopCommerce search path)"
```


---

### Task 8: Casa Rica scraper

**Files:**

* Create: `scrapers/casa_rica.py`
* Test: `tests/test_scraper_casa_rica.py`
* Create: `fixtures/casa_rica_search_arroz.html`

**Interfaces:** same shape as Task 7, `name = "casa_rica"`, `base_url = "https://www.casarica.com.py"`.

**Known constraint:** no `robots.txt` file found (404) — conventionally permissive, ToS still needs the manual check flagged in Task 3 before first live run. Search path unverified (mark with the same `ponytail:` convention as Task 6).

- [ ] **Step 1: Create the fixture** (same structure as Task 7, price `7100`, name `"Arroz Blanco 1kg Casa Rica"`, file `fixtures/casa_rica_search_arroz.html`)
- [ ] **Step 2: Write the failing test**

```python
# tests/test_scraper_casa_rica.py
from scrapers.casa_rica import CasaRicaScraper

def test_search_parses_fixture(monkeypatch):
    scraper = CasaRicaScraper()
    with open("fixtures/casa_rica_search_arroz.html", encoding="utf-8") as f:
        fixture_html = f.read()

    class FakeResponse:
        text = fixture_html
        url = "https://www.casarica.com.py/busqueda?q=arroz"
        def raise_for_status(self):
            pass

    monkeypatch.setattr(scraper.session, "get", lambda *a, **k: FakeResponse())
    results = scraper.search("arroz")
    assert len(results) == 1
    assert results[0].price == 7100.0
```

- [ ] **Step 3: Run test, verify it fails** — `pytest tests/test_scraper_casa_rica.py -v`, expect `ModuleNotFoundError`.
- [ ] **Step 4: Write the implementation**

```python
# scrapers/casa_rica.py
from scrapers.base import ProductMatch, Scraper, extract_jsonld_products


class CasaRicaScraper(Scraper):
    name = "casa_rica"
    base_url = "https://www.casarica.com.py"
    search_path = "/busqueda?q={query}"  # ponytail: no robots.txt found; verify real search path against a live browser session before first production run

    def search(self, query: str) -> list[ProductMatch]:
        url = self.base_url + self.search_path.format(query=query)
        resp = self.session.get(url, timeout=10)
        resp.raise_for_status()
        products = extract_jsonld_products(resp.text)
        return [ProductMatch(p["name"], p["price"], resp.url) for p in products]
```

- [ ] **Step 5: Run test, verify it passes** — `pytest tests/test_scraper_casa_rica.py -v`, expect PASS.
- [ ] **Step 6: Commit**

```bash
git add scrapers/casa_rica.py tests/test_scraper_casa_rica.py fixtures/casa_rica_search_arroz.html
git commit -m "feat: Casa Rica scraper (JSON-LD strategy)"
```


---

### Task 9: Salemma scraper

**Files:**

* Create: `scrapers/salemma.py`
* Test: `tests/test_scraper_salemma.py`
* Create: `fixtures/salemma_search_arroz.html`

**Interfaces:** `name = "salemma"`, `base_url = "https://www.salemmaonline.com.py"`.

**Known constraint:** robots.txt confirmed reachable, disallows only cart/checkout/account/login paths, explicitly allows `?page=` pagination — category/search browsing is not blocked.

- [ ] **Step 1: Create the fixture** (price `6600`, name `"Arroz Blanco 1kg Salemma"`, file `fixtures/salemma_search_arroz.html`, same JSON-LD structure as Task 6).
- [ ] **Step 2: Write the failing test**

```python
# tests/test_scraper_salemma.py
from scrapers.salemma import SalemmaScraper

def test_search_parses_fixture(monkeypatch):
    scraper = SalemmaScraper()
    with open("fixtures/salemma_search_arroz.html", encoding="utf-8") as f:
        fixture_html = f.read()

    class FakeResponse:
        text = fixture_html
        url = "https://www.salemmaonline.com.py/busqueda?q=arroz"
        def raise_for_status(self):
            pass

    monkeypatch.setattr(scraper.session, "get", lambda *a, **k: FakeResponse())
    results = scraper.search("arroz")
    assert len(results) == 1
    assert results[0].price == 6600.0
```

- [ ] **Step 3: Run test, verify it fails.**
- [ ] **Step 4: Write the implementation**

```python
# scrapers/salemma.py
from scrapers.base import ProductMatch, Scraper, extract_jsonld_products


class SalemmaScraper(Scraper):
    name = "salemma"
    base_url = "https://www.salemmaonline.com.py"
    search_path = "/busqueda?q={query}"  # robots.txt confirmed: cart/checkout/account/login disallowed only, search not blocked

    def search(self, query: str) -> list[ProductMatch]:
        url = self.base_url + self.search_path.format(query=query)
        resp = self.session.get(url, timeout=10)
        resp.raise_for_status()
        products = extract_jsonld_products(resp.text)
        return [ProductMatch(p["name"], p["price"], resp.url) for p in products]
```

- [ ] **Step 5: Run test, verify it passes.**
- [ ] **Step 6: Commit**

```bash
git add scrapers/salemma.py tests/test_scraper_salemma.py fixtures/salemma_search_arroz.html
git commit -m "feat: Salemma scraper (JSON-LD strategy)"
```


---

### Task 10: Biggie scraper

**Files:**

* Create: `scrapers/biggie.py`
* Test: `tests/test_scraper_biggie.py`
* Create: `fixtures/biggie_search_arroz.html`

**Interfaces:** `name = "biggie"`, `base_url = "https://www.biggie.com.py"`.

**Known constraint:** confirmed the site is a **Next.js SPA** — a plain `requests.get` on a search page will likely return only the app shell, not product data, unless Next.js server-rendered the JSON-LD into the initial HTML (common even in SPAs for SEO) or there's a `/_next/data/...` JSON endpoint. Implement with the same JSON-LD-first strategy (works if SSR includes it); document the fallback explicitly as a `ponytail:` comment so a human checks it against the live site before trusting it in production.

- [ ] **Step 1: Create the fixture** (price `6700`, name `"Arroz Blanco 1kg Biggie"`, file `fixtures/biggie_search_arroz.html`, same JSON-LD structure as Task 6 — this fixture models the case where Next.js SSR still emits the JSON-LD tag).
- [ ] **Step 2: Write the failing test**

```python
# tests/test_scraper_biggie.py
from scrapers.biggie import BiggieScraper

def test_search_parses_fixture(monkeypatch):
    scraper = BiggieScraper()
    with open("fixtures/biggie_search_arroz.html", encoding="utf-8") as f:
        fixture_html = f.read()

    class FakeResponse:
        text = fixture_html
        url = "https://www.biggie.com.py/buscar?q=arroz"
        def raise_for_status(self):
            pass

    monkeypatch.setattr(scraper.session, "get", lambda *a, **k: FakeResponse())
    results = scraper.search("arroz")
    assert len(results) == 1
    assert results[0].price == 6700.0
```

- [ ] **Step 3: Run test, verify it fails.**
- [ ] **Step 4: Write the implementation**

```python
# scrapers/biggie.py
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
```

- [ ] **Step 5: Run test, verify it passes.**
- [ ] **Step 6: Commit**

```bash
git add scrapers/biggie.py tests/test_scraper_biggie.py fixtures/biggie_search_arroz.html
git commit -m "feat: Biggie scraper (JSON-LD strategy, Next.js SSR dependent)"
```


---

### Task 11: Areté scraper

**Files:**

* Create: `scrapers/arete.py`
* Test: `tests/test_scraper_arete.py`
* Create: `fixtures/arete_search_arroz.html`

**Interfaces:** `name = "arete"`, `base_url = "https://www.arete.com.py"`.

**Known constraint:** no `robots.txt` found (404) — check ToS manually before first live run.

- [ ] **Step 1: Create the fixture** (price `6550`, name `"Arroz Blanco 1kg Areté"`, file `fixtures/arete_search_arroz.html`).
- [ ] **Step 2: Write the failing test**

```python
# tests/test_scraper_arete.py
from scrapers.arete import AreteScraper

def test_search_parses_fixture(monkeypatch):
    scraper = AreteScraper()
    with open("fixtures/arete_search_arroz.html", encoding="utf-8") as f:
        fixture_html = f.read()

    class FakeResponse:
        text = fixture_html
        url = "https://www.arete.com.py/busqueda?q=arroz"
        def raise_for_status(self):
            pass

    monkeypatch.setattr(scraper.session, "get", lambda *a, **k: FakeResponse())
    results = scraper.search("arroz")
    assert len(results) == 1
    assert results[0].price == 6550.0
```

- [ ] **Step 3: Run test, verify it fails.**
- [ ] **Step 4: Write the implementation**

```python
# scrapers/arete.py
from scrapers.base import ProductMatch, Scraper, extract_jsonld_products


class AreteScraper(Scraper):
    name = "arete"
    base_url = "https://www.arete.com.py"
    search_path = "/busqueda?q={query}"  # ponytail: no robots.txt found; verify real search path against a live browser session before first production run

    def search(self, query: str) -> list[ProductMatch]:
        url = self.base_url + self.search_path.format(query=query)
        resp = self.session.get(url, timeout=10)
        resp.raise_for_status()
        products = extract_jsonld_products(resp.text)
        return [ProductMatch(p["name"], p["price"], resp.url) for p in products]
```

- [ ] **Step 5: Run test, verify it passes.**
- [ ] **Step 6: Commit**

```bash
git add scrapers/arete.py tests/test_scraper_arete.py fixtures/arete_search_arroz.html
git commit -m "feat: Areté scraper (JSON-LD strategy)"
```


---

### Task 12: Grütter scraper

**Files:**

* Create: `scrapers/grutter.py`
* Test: `tests/test_scraper_grutter.py`
* Create: `fixtures/grutter_search_arroz.html`

**Interfaces:** `name = "grutter"`, `base_url = "https://grutteronline.casagrutter.com.py"`.

**Known constraint:** this domain was **unreachable from the planning sandbox** (connection failure, not an HTTP error) — confirm basic reachability from the real execution environment before relying on this scraper in `run_daily.py` (Task 17); if it's still unreachable there too, exclude it from the aggregate index the same way as Superseis, via the per-site error handling built in Task 17.

- [ ] **Step 1: Create the fixture** (price `6400`, name `"Arroz Blanco 1kg Grütter"`, file `fixtures/grutter_search_arroz.html`).
- [ ] **Step 2: Write the failing test**

```python
# tests/test_scraper_grutter.py
from scrapers.grutter import GrutterScraper

def test_search_parses_fixture(monkeypatch):
    scraper = GrutterScraper()
    with open("fixtures/grutter_search_arroz.html", encoding="utf-8") as f:
        fixture_html = f.read()

    class FakeResponse:
        text = fixture_html
        url = "https://grutteronline.casagrutter.com.py/busqueda?q=arroz"
        def raise_for_status(self):
            pass

    monkeypatch.setattr(scraper.session, "get", lambda *a, **k: FakeResponse())
    results = scraper.search("arroz")
    assert len(results) == 1
    assert results[0].price == 6400.0
```

- [ ] **Step 3: Run test, verify it fails.**
- [ ] **Step 4: Write the implementation**

```python
# scrapers/grutter.py
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
```

- [ ] **Step 5: Run test, verify it passes.**
- [ ] **Step 6: Commit**

```bash
git add scrapers/grutter.py tests/test_scraper_grutter.py fixtures/grutter_search_arroz.html
git commit -m "feat: Grütter scraper (JSON-LD strategy)"
```


---

### Task 13: Los Jardines scraper

**Files:**

* Create: `scrapers/los_jardines.py`
* Test: `tests/test_scraper_los_jardines.py`
* Create: `fixtures/los_jardines_search_arroz.html`

**Interfaces:** `name = "los_jardines"`, `base_url = "https://www.losjardinesonline.com.py"`.

**Known constraint:** no `robots.txt` found (404) — check ToS manually before first live run.

- [ ] **Step 1: Create the fixture** (price `6350`, name `"Arroz Blanco 1kg Los Jardines"`, file `fixtures/los_jardines_search_arroz.html`).
- [ ] **Step 2: Write the failing test**

```python
# tests/test_scraper_los_jardines.py
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
```

- [ ] **Step 3: Run test, verify it fails.**
- [ ] **Step 4: Write the implementation**

```python
# scrapers/los_jardines.py
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
```

- [ ] **Step 5: Run test, verify it passes.**
- [ ] **Step 6: Commit**

```bash
git add scrapers/los_jardines.py tests/test_scraper_los_jardines.py fixtures/los_jardines_search_arroz.html
git commit -m "feat: Los Jardines scraper (JSON-LD strategy)"
```


---

### Task 14: Real scraper

**Files:**

* Create: `scrapers/real.py`
* Test: `tests/test_scraper_real.py`
* Create: `fixtures/real_search_arroz.html`

**Interfaces:** `name = "real"`, `base_url = "https://www.realonline.com.py"`.

**Known constraint:** robots.txt confirmed reachable, declares `Content-Signal: search=yes,ai-train=no,use=reference` — explicitly permits this project's use case (reference dataset, not AI training). Cite this in the README/paper.

- [ ] **Step 1: Create the fixture** (price `6250`, name `"Arroz Blanco 1kg Real"`, file `fixtures/real_search_arroz.html`).
- [ ] **Step 2: Write the failing test**

```python
# tests/test_scraper_real.py
from scrapers.real import RealScraper

def test_search_parses_fixture(monkeypatch):
    scraper = RealScraper()
    with open("fixtures/real_search_arroz.html", encoding="utf-8") as f:
        fixture_html = f.read()

    class FakeResponse:
        text = fixture_html
        url = "https://www.realonline.com.py/busqueda?q=arroz"
        def raise_for_status(self):
            pass

    monkeypatch.setattr(scraper.session, "get", lambda *a, **k: FakeResponse())
    results = scraper.search("arroz")
    assert len(results) == 1
    assert results[0].price == 6250.0
```

- [ ] **Step 3: Run test, verify it fails.**
- [ ] **Step 4: Write the implementation**

```python
# scrapers/real.py
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
```

- [ ] **Step 5: Run test, verify it passes.**
- [ ] **Step 6: Commit**

```bash
git add scrapers/real.py tests/test_scraper_real.py fixtures/real_search_arroz.html
git commit -m "feat: Real scraper (JSON-LD strategy)"
```


---

### Task 15: Outlier detection (`outliers.py`)

**Files:**

* Create: `outliers.py`
* Test: `tests/test_outliers.py`

**Interfaces:**

```python
# tests/test_outliers.py
from outliers import is_outlier

def test_no_outlier_with_stable_prices():
    history = [6500.0, 6520.0, 6480.0, 6510.0, 6495.0]
    assert is_outlier(history, 6505.0) is False

def test_flags_a_price_spike():
    history = [6500.0, 6520.0, 6480.0, 6510.0, 6495.0]
    assert is_outlier(history, 65000.0) is True  # 10x jump

def test_flags_a_price_crash():
    history = [6500.0, 6520.0, 6480.0, 6510.0, 6495.0]
    assert is_outlier(history, 650.0) is True  # 10x drop

def test_insufficient_history_never_flags():
    assert is_outlier([6500.0], 65000.0) is False
    assert is_outlier([], 65000.0) is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_outliers.py -v` Expected: FAIL with `ModuleNotFoundError: No module named 'outliers'`

- [ ] **Step 3: Write the implementation**

```python
# outliers.py
import math
import statistics


def is_outlier(history: list[float], new_price: float, threshold: float = 3.5) -> bool:
    """Flag new_price as an outlier relative to history using a robust
    z-score (MAD-based) on the log price. Returns False if there isn't
    enough history (< 3 points) to judge.
    """
    if len(history) < 3 or new_price <= 0:
        return False

    log_history = [math.log(p) for p in history if p > 0]
    if len(log_history) < 3:
        return False

    median = statistics.median(log_history)
    deviations = [abs(x - median) for x in log_history]
    mad = statistics.median(deviations)

    if mad == 0:
        # no variation in history at all — flag any change as an outlier
        return math.log(new_price) != median

    # 0.6745 makes MAD comparable to a standard deviation for normal data
    robust_z = abs((math.log(new_price) - median) * 0.6745 / mad)
    return robust_z > threshold
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_outliers.py -v` Expected: PASS (4 tests)

- [ ] **Step 5: Commit**

```bash
git add outliers.py tests/test_outliers.py
git commit -m "feat: MAD-based outlier detection on log price changes"
```


---

### Task 16: Weighted Jevons index (`index.py`)

**Files:**

* Create: `index.py`
* Test: `tests/test_index.py`

**Interfaces:**

```python
# tests/test_index.py
import db
import index

TOY_BASKET = [
    {"product_key": "arroz", "bcp_category": "cereales", "weight": 0.6},
    {"product_key": "aceite", "bcp_category": "aceites", "weight": 0.4},
]


def _seed(conn):
    # Day 1: base prices. Day 2: arroz +10%, aceite unchanged.
    db.insert_price(conn, "2026-07-01", "stock", "arroz", "Arroz", 100.0, "u")
    db.insert_price(conn, "2026-07-01", "stock", "aceite", "Aceite", 200.0, "u")
    db.insert_price(conn, "2026-07-02", "stock", "arroz", "Arroz", 110.0, "u")
    db.insert_price(conn, "2026-07-02", "stock", "aceite", "Aceite", 200.0, "u")


def test_compute_daily_index_single_supermarket(tmp_path):
    conn = db.connect(str(tmp_path / "t.db"))
    db.init_schema(conn)
    _seed(conn)

    result = index.compute_daily_index(conn, TOY_BASKET, "stock")

    assert result["2026-07-01"] == 100.0
    # weighted geometric mean of (1.10 for arroz, 1.00 for aceite) with weights 0.6/0.4
    expected_change = 1.10 ** 0.6 * 1.00 ** 0.4
    assert abs(result["2026-07-02"] - 100.0 * expected_change) < 1e-6


def test_compute_daily_index_excludes_outliers(tmp_path):
    conn = db.connect(str(tmp_path / "t.db"))
    db.init_schema(conn)
    _seed(conn)
    # Day 2 arroz price flagged as an outlier — should be excluded from the change
    db.insert_price(conn, "2026-07-02", "stock", "arroz", "Arroz", 110.0, "u", is_outlier=True)

    result = index.compute_daily_index(conn, TOY_BASKET, "stock")
    # only aceite (unchanged) contributes -> index stays at 100
    assert abs(result["2026-07-02"] - 100.0) < 1e-6


def test_compute_aggregate_index_averages_supermarkets(tmp_path):
    conn = db.connect(str(tmp_path / "t.db"))
    db.init_schema(conn)
    _seed(conn)
    db.insert_price(conn, "2026-07-01", "salemma", "arroz", "Arroz", 100.0, "u")
    db.insert_price(conn, "2026-07-01", "salemma", "aceite", "Aceite", 200.0, "u")
    db.insert_price(conn, "2026-07-02", "salemma", "arroz", "Arroz", 100.0, "u")  # no change at salemma
    db.insert_price(conn, "2026-07-02", "salemma", "aceite", "Aceite", 200.0, "u")

    result = index.compute_aggregate_index(conn, TOY_BASKET, ["stock", "salemma"])
    assert result["2026-07-01"] == 100.0
    stock_day2 = 100.0 * (1.10 ** 0.6 * 1.00 ** 0.4)
    salemma_day2 = 100.0
    assert abs(result["2026-07-02"] - (stock_day2 + salemma_day2) / 2) < 1e-6
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_index.py -v` Expected: FAIL with `ModuleNotFoundError: No module named 'index'`

- [ ] **Step 3: Write the implementation**

```python
# index.py
import math
import statistics

import db


def _prices_by_date(conn, supermarket: str, product_key: str) -> dict[str, float]:
    rows = db.read_prices(conn, product_key=product_key, supermarket=supermarket)
    return {r["date"]: r["price"] for r in rows if not r["is_outlier"]}


def compute_daily_index(conn, basket: list[dict], supermarket: str) -> dict[str, float]:
    per_product_prices = {
        item["product_key"]: _prices_by_date(conn, supermarket, item["product_key"])
        for item in basket
    }
    all_dates = sorted({d for prices in per_product_prices.values() for d in prices})
    if not all_dates:
        return {}

    result: dict[str, float] = {all_dates[0]: 100.0}
    for prev_date, date in zip(all_dates, all_dates[1:]):
        ratios_weights: list[tuple[float, float]] = []
        for item in basket:
            prices = per_product_prices[item["product_key"]]
            if prev_date in prices and date in prices and prices[prev_date] > 0:
                ratios_weights.append((prices[date] / prices[prev_date], item["weight"]))

        if not ratios_weights:
            change = 1.0
        else:
            total_weight = sum(w for _, w in ratios_weights)
            log_change = sum(w * math.log(r) for r, w in ratios_weights) / total_weight
            change = math.exp(log_change)

        result[date] = result[prev_date] * change

    return result


def compute_aggregate_index(conn, basket: list[dict], supermarkets: list[str]) -> dict[str, float]:
    per_market = {sm: compute_daily_index(conn, basket, sm) for sm in supermarkets}
    all_dates = sorted({d for series in per_market.values() for d in series})
    aggregate: dict[str, float] = {}
    for date in all_dates:
        values = [series[date] for series in per_market.values() if date in series]
        if values:
            aggregate[date] = statistics.fmean(values)

    for sm, series in per_market.items():
        for date, value in series.items():
            db.write_index_daily(conn, date, sm, value)
    for date, value in aggregate.items():
        db.write_index_daily(conn, date, "AGREGADO", value)

    return aggregate
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_index.py -v` Expected: PASS (3 tests)

- [ ] **Step 5: Commit**

```bash
git add index.py tests/test_index.py
git commit -m "feat: weighted Jevons price index (per-supermarket and aggregate)"
```


---

### Task 17: Daily orchestrator (`run_daily.py`)

**Files:**

* Create: `run_daily.py`
* Test: `tests/test_run_daily.py`

**Interfaces:**

```python
# tests/test_run_daily.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_run_daily.py -v` Expected: FAIL with `ModuleNotFoundError: No module named 'run_daily'`

- [ ] **Step 3: Write the implementation**

```python
# run_daily.py
import json
import logging

import db
import index
import outliers
from scrapers.base import Scraper

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("run_daily")


def run(conn, basket: list[dict], scrapers: list[Scraper], date: str) -> dict:
    inserted = 0
    missing = 0
    failed_supermarkets: list[str] = []

    for scraper in scrapers:
        try:
            for item in basket:
                query = item["queries"].get(scraper.name, item["nombre_canonico"])
                matches = scraper.search(query)
                if not matches:
                    missing += 1
                    log.info("no match for %s on %s", item["product_key"], scraper.name)
                    continue

                best = matches[0]
                history = [
                    r["price"]
                    for r in db.read_prices(conn, product_key=item["product_key"], supermarket=scraper.name)
                ]
                flagged = outliers.is_outlier(history, best.price)
                db.insert_price(
                    conn, date, scraper.name, item["product_key"], best.name, best.price, best.url,
                    is_outlier=flagged,
                )
                inserted += 1
        except Exception as exc:  # a whole supermarket failing must not abort the run
            log.warning("supermarket %s failed: %s", scraper.name, exc)
            failed_supermarkets.append(scraper.name)

    return {"inserted": inserted, "missing": missing, "failed_supermarkets": failed_supermarkets}


def export_json_csv(conn, prices_json_path: str, prices_csv_path: str, index_json_path: str) -> None:
    rows = db.read_prices(conn)
    with open(prices_json_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)

    if rows:
        import csv

        with open(prices_csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

    # Separate from prices.json (raw price rows, the dataset proper) because
    # the dashboard (Task 21) only needs the much smaller index_daily series —
    # fetching the full price history client-side would be wasteful.
    index_rows = db.read_index_daily(conn)
    with open(index_json_path, "w", encoding="utf-8") as f:
        json.dump({"index_daily": index_rows}, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    import datetime

    from scrapers.arete import AreteScraper
    from scrapers.biggie import BiggieScraper
    from scrapers.casa_rica import CasaRicaScraper
    from scrapers.grutter import GrutterScraper
    from scrapers.los_jardines import LosJardinesScraper
    from scrapers.real import RealScraper
    from scrapers.salemma import SalemmaScraper
    from scrapers.stock import StockScraper
    from scrapers.superseis import SuperseisScraper

    with open("basket.json", encoding="utf-8") as f:
        basket_data = json.load(f)

    all_scrapers = [
        SuperseisScraper(), StockScraper(), CasaRicaScraper(), SalemmaScraper(),
        BiggieScraper(), AreteScraper(), GrutterScraper(), LosJardinesScraper(), RealScraper(),
    ]

    conn = db.connect("prices.db")
    db.init_schema(conn)
    today = datetime.date.today().isoformat()

    summary = run(conn, basket_data, all_scrapers, today)
    log.info("run summary: %s", summary)

    index.compute_aggregate_index(conn, basket_data, [s.name for s in all_scrapers])
    export_json_csv(conn, "prices.json", "prices.csv", "index.json")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_run_daily.py -v` Expected: PASS (1 test)

- [ ] **Step 5: Commit**

```bash
git add run_daily.py tests/test_run_daily.py
git commit -m "feat: daily orchestrator — scrape all sites, isolate failures, update index, export"
```


---

### Task 18: GitHub Actions workflow & release distribution

**Files:**

* Create: `.github/workflows/scrape.yml`

**Interfaces:**

```yaml
# .github/workflows/scrape.yml
name: Scrape prices and update dataset

on:
  schedule:
    - cron: "0 11 * * *"  # ~08:00 America/Asuncion
  workflow_dispatch: {}

permissions:
  contents: write

jobs:
  scrape:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Download existing dataset (if any)
        run: |
          gh release download dataset --pattern "prices.db" --dir . --clobber || echo "no existing release yet"
        env:
          GH_TOKEN: ${{ github.token }}

      - name: Run daily scrape
        run: python run_daily.py

      - name: Ensure release exists
        run: |
          gh release view dataset || gh release create dataset --title "Hepy dataset" --notes "Auto-updated daily by scrape.yml. Licensed CC BY 4.0 — see LICENSE-DATA."
        env:
          GH_TOKEN: ${{ github.token }}

      - name: Upload updated dataset
        run: gh release upload dataset prices.db prices.csv prices.json index.json --clobber
        env:
          GH_TOKEN: ${{ github.token }}
```

- [ ] **Step 2: Verify the YAML is well-formed**

Run: `python -c "import yaml; yaml.safe_load(open('.github/workflows/scrape.yml'))"` Expected: no exception (requires `pyyaml`; if not installed, run `pip install pyyaml` first just for this check — it's not a project dependency).

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/scrape.yml
git commit -m "ci: daily scrape workflow, publishes dataset to a GitHub Release"
```


---

### Task 19: Validation against official IPC-BCP (`validation.py`)

**Files:**

* Create: `validation.py`
* Test: `tests/test_validation.py`

**Interfaces:**

```python
# tests/test_validation.py
from validation import correlate_with_official


def test_perfect_correlation_at_zero_lag():
    hepy = {"2026-01-01": 100.0, "2026-01-02": 101.0, "2026-01-03": 102.0, "2026-01-04": 103.0}
    ipc = {"2026-01-01": 200.0, "2026-01-02": 202.0, "2026-01-03": 204.0, "2026-01-04": 206.0}

    result = correlate_with_official(hepy, ipc, max_lag_days=2)
    assert result["best_lag_days"] == 0
    assert result["correlation"] > 0.99


def test_no_overlapping_dates_returns_none_correlation():
    hepy = {"2020-01-01": 100.0}
    ipc = {"2030-01-01": 200.0}
    result = correlate_with_official(hepy, ipc, max_lag_days=1)
    assert result["correlation"] is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_validation.py -v` Expected: FAIL with `ModuleNotFoundError: No module named 'validation'`

- [ ] **Step 3: Write the implementation**

```python
# validation.py
import datetime
import statistics


def _shift_date(date_str: str, days: int) -> str:
    d = datetime.date.fromisoformat(date_str) + datetime.timedelta(days=days)
    return d.isoformat()


def _pearson(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 2 or len(ys) < 2:
        return None
    mean_x, mean_y = statistics.fmean(xs), statistics.fmean(ys)
    num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    den_x = sum((x - mean_x) ** 2 for x in xs) ** 0.5
    den_y = sum((y - mean_y) ** 2 for y in ys) ** 0.5
    if den_x == 0 or den_y == 0:
        return None
    return num / (den_x * den_y)


def correlate_with_official(
    hepy_series: dict[str, float], ipc_series: dict[str, float], max_lag_days: int = 30
) -> dict:
    best_lag = 0
    best_corr: float | None = None

    for lag in range(-max_lag_days, max_lag_days + 1):
        xs, ys = [], []
        for date, hepy_value in hepy_series.items():
            shifted = _shift_date(date, lag)
            if shifted in ipc_series:
                xs.append(hepy_value)
                ys.append(ipc_series[shifted])
        corr = _pearson(xs, ys)
        if corr is not None and (best_corr is None or abs(corr) > abs(best_corr)):
            best_corr = corr
            best_lag = lag

    return {"best_lag_days": best_lag, "correlation": best_corr}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_validation.py -v` Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add validation.py tests/test_validation.py
git commit -m "feat: correlate Hepy index against official IPC-BCP series with optimal lag"
```


---

### Task 20: Phase 2 scaffolding (`forecasting/`)

**Files:**

* Create: `forecasting/__init__.py` (empty)
* Create: `forecasting/features.py`
* Create: `forecasting/models.py`
* Test: `tests/test_forecasting_features.py`

**Interfaces:**

```python
# tests/test_forecasting_features.py
import db
import forecasting.features as features


def test_build_feature_table_computes_lags(tmp_path):
    conn = db.connect(str(tmp_path / "t.db"))
    db.init_schema(conn)
    for i, value in enumerate([100.0, 101.0, 102.0, 103.0], start=1):
        db.write_index_daily(conn, f"2026-01-0{i}", "AGREGADO", value)

    rows = features.build_feature_table(conn, supermarket="AGREGADO", lags=[1])
    by_date = {r["date"]: r for r in rows}

    assert by_date["2026-01-01"]["lag_1"] is None
    assert by_date["2026-01-02"]["lag_1"] == 100.0
    assert by_date["2026-01-04"]["lag_1"] == 102.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_forecasting_features.py -v` Expected: FAIL with `ModuleNotFoundError: No module named 'forecasting'`

- [ ] **Step 3: Write the implementation**

```python
# forecasting/features.py
import db


def build_feature_table(conn, supermarket: str = "AGREGADO", lags: list[int] | None = None) -> list[dict]:
    lags = lags or [1, 7, 30]
    series = db.read_index_daily(conn, supermarket=supermarket)
    dates = [r["date"] for r in series]
    values = {r["date"]: r["value"] for r in series}

    rows: list[dict] = []
    for i, date in enumerate(dates):
        row = {"date": date, "index_value": values[date]}
        for lag in lags:
            row[f"lag_{lag}"] = values[dates[i - lag]] if i - lag >= 0 else None
        rows.append(row)
    return rows
```

```python
# forecasting/models.py
"""Fase 2 — nowcasting del IPC-BCP oficial. No implementar hasta acumular
6-12 meses de historia en prices.db / index_daily (ver design doc
2026-07-22-hepy-indice-precios-design, sección "Fase 2").
"""


def ridge_baseline(feature_table: list[dict], target: list[float]):
    """Planned: sklearn.linear_model.RidgeCV sobre feature_table (ver
    forecasting.features.build_feature_table) contra la variación
    intermensual del IPC-BCP oficial. Punto de partida interpretable.
    """
    raise NotImplementedError("Fase 2 — esperar 6-12 meses de historia acumulada")


def gbm_baseline(feature_table: list[dict], target: list[float]):
    """Planned: XGBoost o LightGBM sobre las mismas features que ridge_baseline.
    Es el modelo que domina la literatura reciente de nowcasting de inflación
    en economías en desarrollo (ver Bolivar 2025 en el design doc)."""
    raise NotImplementedError("Fase 2 — esperar 6-12 meses de historia acumulada")


def sarimax_baseline(index_series: list[float]):
    """Planned: statsmodels SARIMAX como benchmark econométrico clásico,
    obligatorio para poder decir "el modelo de ML mejora sobre X%"."""
    raise NotImplementedError("Fase 2 — esperar 6-12 meses de historia acumulada")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_forecasting_features.py -v` Expected: PASS (1 test)

- [ ] **Step 5: Commit**

```bash
git add forecasting/ tests/test_forecasting_features.py
git commit -m "feat: Phase 2 scaffolding — feature table builder + documented model stubs"
```


---

### Task 21: Static dashboard for Cloudflare Pages (`dashboard/`)

**Revision note:** originally spec'd as a Streamlit app; changed to a static
site (Cloudflare Pages runs static files + edge Workers, not a persistent
Python server, so Streamlit is not deployable there). The dashboard fetches
`index.json` directly from the GitHub Release client-side — no build step,
no server, no new Python dependency (Task 17 already produces
`index.json` via `export_json_csv`).

**Files:**

* Create: `dashboard/index.html`
* Create: `dashboard/app.js`

**Interfaces:**

```html
<!-- dashboard/index.html -->
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <title>Hepy — índice de precios Paraguay</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js"
          integrity="sha384-REPLACE_WITH_COMPUTED_HASH" crossorigin="anonymous"></script>
</head>
<body>
  <h1>Hepy 🧺</h1>
  <p>Índice de precios de alta frecuencia para Paraguay — Koeti Labs</p>

  <h2>Índice agregado (base 100)</h2>
  <canvas id="aggregate-chart"></canvas>

  <h2>Por supermercado</h2>
  <div id="supermarket-charts"></div>

  <h2>Descargar dataset (CC BY 4.0 — citar la fuente)</h2>
  <ul id="downloads"></ul>

  <script src="app.js"></script>
</body>
</html>
```

```javascript
// dashboard/app.js
const DATASET_RELEASE_BASE = "https://github.com/koeti-labs/hepy/releases/download/dataset";

async function loadIndexData() {
  const res = await fetch(`${DATASET_RELEASE_BASE}/index.json`);
  return res.json();
}

function lineChart(canvasId, labels, values, label) {
  new Chart(document.getElementById(canvasId), {
    type: "line",
    data: { labels, datasets: [{ label, data: values }] },
  });
}

async function main() {
  const data = await loadIndexData();
  const indexDaily = data.index_daily || [];

  const aggregate = indexDaily.filter(r => r.supermarket === "AGREGADO");
  if (aggregate.length === 0) {
    document.body.insertAdjacentHTML("beforeend", "<p>Todavía no hay datos del índice agregado.</p>");
  } else {
    lineChart("aggregate-chart", aggregate.map(r => r.date), aggregate.map(r => r.value), "Índice");
  }

  const supermarkets = [...new Set(indexDaily.map(r => r.supermarket).filter(s => s !== "AGREGADO"))].sort();
  const container = document.getElementById("supermarket-charts");
  for (const sm of supermarkets) {
    const canvas = document.createElement("canvas");
    canvas.id = `chart-${sm}`;
    container.appendChild(canvas);
    const series = indexDaily.filter(r => r.supermarket === sm);
    lineChart(canvas.id, series.map(r => r.date), series.map(r => r.value), sm);
  }

  const downloads = document.getElementById("downloads");
  for (const [fname, label] of [["prices.db", "SQLite"], ["prices.csv", "CSV"], ["prices.json", "JSON (precios)"], ["index.json", "JSON (índice)"]]) {
    downloads.insertAdjacentHTML("beforeend", `<li><a href="${DATASET_RELEASE_BASE}/${fname}">${label}</a></li>`);
  }
}

main();
```

- [ ] **Step 1b: Pin Subresource Integrity for the Chart.js CDN script**

Replace `REPLACE_WITH_COMPUTED_HASH` in `index.html` with the real SRI hash
for the pinned Chart.js version (`4.4.4`), computed via:
`curl -s https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js | openssl dgst -sha384 -binary | openssl base64 -A`
(prefix the result with `sha384-`). Do not leave the placeholder in the
committed file, and do not load the CDN script without an `integrity` +
`crossorigin="anonymous"` attribute — loading external JS unpinned exposes
the dashboard to CDN compromise.

- [ ] **Step 2: Smoke-test locally**

Serve the folder with a plain static server (e.g. `python -m http.server` from
inside `dashboard/`) and open it in a browser. Expected: if no release exists
yet, the `fetch` to `index.json` fails — confirm the page shows the "no hay
datos" message instead of a silent blank page (i.e. add a `.catch` around the
fetch that renders that message). Once a real release exists (post Task 18),
confirm the aggregate and per-supermarket charts render and the three
download links point at real files.

- [ ] **Step 3: Cloudflare Pages config**

Add a `dashboard/README.md` (or a section in the root `README.md`) noting
the Cloudflare Pages build settings: build command `(none)`, output
directory `dashboard`. No `wrangler.toml` needed for a plain static Pages
project with no Functions.

- [ ] **Step 4: Commit**

```bash
git add dashboard/
git commit -m "feat: static dashboard (Chart.js) for Cloudflare Pages deployment"
```


---

### Task 22: README finalization & end-to-end smoke test

**Files:**

* Modify: `README.md`
* Test: manual (documented below, no new automated test — this task verifies the *integration* of every previous task, which already have their own unit tests)

**Interfaces:** none new — this task wires together everything already built and confirms it as a whole.

- [ ] **Step 1: Run the full test suite**

Run: `pytest -v` Expected: every test from Tasks 2, 4, 5, 6-14, 15, 16, 17, 19, 20 passes (30+ tests total).

- [ ] **Step 2: Run** `**run_daily.py**` **once end-to-end against the real sites**

Run: `python run_daily.py` Expected: exits without raising; check the printed summary log — some supermarkets may appear in `failed_supermarkets` (expected for Superseis/Grütter per the Task 3 findings, until reconfirmed from a real network); `prices.db`, `prices.csv`, `prices.json`, `index.json` are created in the repo root.

- [ ] **Step 3: Expand** `**README.md**` **with the real usage instructions**

```markdown
## Hepy

Índice de precios de alta frecuencia para Paraguay, construido con scraping diario
de 9 supermercados online (Superseis, Stock, Casa Rica, Salemma, Biggie, Areté,
Grütter, Los Jardines, Real), ponderado con la metodología del IPC del Banco
Central del Paraguay (BCP, base diciembre 2017, EPF 2015-2016), y validado
empíricamente contra la serie oficial.

- Código: Apache-2.0 (`LICENSE-CODE`)
- Dataset: CC BY 4.0 (`LICENSE-DATA`) — citar como "Hepy — Koeti Labs (<año>), <URL del dataset>"
- Dataset descargable: [Releases → dataset](../../releases/tag/dataset) (`prices.db`, `prices.csv`, `prices.json`, `index.json`)
- Dashboard: sitio estático (`dashboard/`), desplegado en Cloudflare Pages — servir localmente con `python -m http.server` desde `dashboard/`

### Desarrollo

    pip install -r requirements.txt
    pytest
    python run_daily.py       # corre el scraper una vez, localmente
    cd dashboard && python -m http.server

### Estado del proyecto

Fase 1 (scraper + índice ponderado + validación contra el IPC-BCP + detección de
outliers) implementada. Fase 2 (nowcasting con ML) tiene el andamiaje de features
listo (`forecasting/`) pero los modelos no se entrenan todavía — requiere 6-12
meses de historia acumulada en el dataset.

Ver `legal/revision_tos.md` para el detalle de la revisión legal por sitio.
```

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs: finalize README with usage, licensing, and project status"
```


---

## Self-review notes (kept for the record, already applied above)

* **Spec coverage:** every section of the design doc has a task — scaffolding/licenses (1), schema (2), legal (3), canasta (4), scraper interface (5), 9 scrapers (6-14), outliers (15), index (16), orchestrator (17), distribution (18), validation (19), Phase 2 scaffold (20), dashboard (21), docs/E2E (22).
* **Placeholder scan:** an earlier draft of `index.py` in Task 16 contained a dead/nonsensical line during drafting; it was removed before finalizing this document — the version above is the corrected, final one to type in.
* **Type consistency:** `ProductMatch(name, price, url)` is used identically in Tasks 5-14; `Scraper.search(self, query: str) -> list[ProductMatch]` signature is identical everywhere; `db.insert_price(conn, date, supermarket, product_key, product_name, price, url, is_outlier=False)` argument order matches every call site in Tasks 6-17.
