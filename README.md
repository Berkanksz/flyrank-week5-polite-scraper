# FlyRank Backend Internship - Week 5: The polite scraper

A respectful, deterministic scraping pipeline built in **Python** using `requests`, `BeautifulSoup4`, and `pydantic`. It crawls the first 3 catalogue pages of Books to Scrape, visits all 60 book detail pages, turns messy HTML into clean, checked JSON records, handles failures gracefully without crashing, and writes an honest run report at the end.

---

## Target Classification
- **Target Site:** [Books to Scrape](https://books.toscrape.com/)
- **Why this site:** Books to Scrape is explicitly built and hosted as a sandbox for learning and practising web scraping.
- **Scope:** The first 3 catalogue pages only (discovering 60 unique books).
- **robots.txt result:** Request to `https://books.toscrape.com/robots.txt` returned HTTP 404 (no robots file found). A missing file is not automatic permission, but the site's homepage explicitly grants permission for scraping practice.
- **Commitment:** *"I will not reuse this code on another site without checking its rules and terms first."*

---

## Politeness Rules
1. **Honest User-Agent:** Every request sends `User-Agent: FlyRankInternship-A9/1.0 (+https://github.com/Berkanksz/flyrank-week5-polite-scraper)` so server administrators know who is calling.
2. **Rate Limiting (Polite Delay):** Enforces a minimum 0.5s pause between consecutive network requests.
3. **Timeouts:** All requests timeout after 10 seconds — never hang indefinitely.
4. **Local File Caching:** All fetched HTML pages are stored in `cache/` (git-ignored). Once a page is cached, repeated runs never hit the remote server.
5. **No Browser Overhead:** The target site delivers static server-rendered HTML. Running a headless browser (Puppeteer / Playwright) would only waste bandwidth, memory, and CPU for zero benefit.

---

## Record Schema (Pydantic)
Every book is validated against `BookRecord` before writing to `output/books.json`:

```python
class BookRecord(BaseModel):
    title: str
    product_url: str                # Absolute URL (starts with http:// or https://)
    price_text: str                 # Raw scraped text e.g. "£51.77"
    price_gbp: float                # Clean numeric float e.g. 51.77
    availability_text: str          # e.g. "In stock (22 available)"
    rating_text: str                # e.g. "Three"
    description: str | None = None  # None if missing, never made-up text
    source_page: str                # Provenance: catalogue page where discovered
    fetched_at: str                 # Provenance: UTC ISO-8601 timestamp
```

Invalid records are diverted to `output/errors.json` and never enter `books.json`.

---

## How to Install and Run

### 1. Requirements
- Python 3.10+

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Pipeline (One Command)
```bash
python main.py
```

### 4. Test Failure Survival Mode
Simulate a broken page by injecting a fake URL (proves 1 bad page doesn't crash the 60 good records):
```bash
python main.py --test-failure
```

---

## Real Run Report (`output/run-report.json`)
```json
{
  "start_time": "2026-10-13T08:58:05.590333Z",
  "duration_seconds": 0.327,
  "catalogue_pages": 3,
  "discovered_urls": 60,
  "unique_urls": 60,
  "pages_fetched": 0,
  "cache_hits": 63,
  "valid_records": 60,
  "invalid_records": 0,
  "failed_pages": 0,
  "errors": []
}
```

---

## Sample Record from `output/books.json`
```json
{
  "title": "A Light in the Attic",
  "product_url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
  "price_text": "£51.77",
  "price_gbp": 51.77,
  "availability_text": "In stock (22 available)",
  "rating_text": "Three",
  "description": "It's hard to imagine a world without A Light in the Attic. This now-classic collection of poetry and drawings from Shel Silverstein celebrates its 20th anniversary with this special edition...",
  "source_page": "https://books.toscrape.com/catalogue/page-1.html",
  "fetched_at": "2026-10-13T08:54:58.549533Z"
}
```

---

## Ethics Note
1. **Always prefer an official API** when one is provided.
2. **Never bypass logins, paywalls, or rate-limit blocks.**
3. **Collect only what is needed** for the specific feature or task.
4. **Be respectful to servers:** cache responses locally, rate limit requests, and never flood resources.

---

## Known Limitation
The current scraper is single-threaded and relies on synchronous requests with a 0.5s pause. For massive multi-thousand page crawls, asynchronous queues (e.g. `asyncio` + `httpx` or Celery) with token-bucket concurrency rate limits would be necessary.
