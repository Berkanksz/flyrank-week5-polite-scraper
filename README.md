# FlyRank Backend Internship - Week 5: The polite scraper

A respectful, deterministic scraping pipeline that extracts 60 books across the first 3 catalogue pages of Books to Scrape, normalizes fields, validates against a Pydantic schema, handles failures gracefully, and outputs a run report.

---

## Target Classification
- **Target Site:** [Books to Scrape](https://books.toscrape.com/)
- **Why this site:** Books to Scrape is explicitly built and hosted as a public practice sandbox for web scraping.
- **Scope:** Exactly the first 3 catalogue pages (60 book detail pages total).
- **Data Collected:** Book title, product URL, raw price text, normalized price in GBP (`price_gbp`), availability, star rating, description, source catalogue page, and fetch timestamp.
- **robots.txt result:** Request to `https://books.toscrape.com/robots.txt` returned HTTP 404 (no robots file found). A missing file is not automatic permission, but the site's homepage explicitly grants permission for scraping practice.
- **Commitment:** *"I will not reuse this code on another site without checking its rules and terms first."*
