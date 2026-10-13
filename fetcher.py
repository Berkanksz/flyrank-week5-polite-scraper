import hashlib
import os
import time
from pathlib import Path
import requests

CACHE_DIR = Path("cache")
USER_AGENT = "FlyRankInternship-A9/1.0 (+https://github.com/Berkanksz/flyrank-week5-polite-scraper)"
TIMEOUT_SECONDS = 10
DELAY_SECONDS = 0.5

# Track stats for the run report
stats = {
    "pages_fetched": 0,
    "cache_hits": 0,
    "failed_pages": 0,
    "errors": []
}

_last_request_time = 0.0


def _url_to_cache_path(url: str, custom_filename: str | None = None) -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    if custom_filename:
        return CACHE_DIR / custom_filename
    h = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
    return CACHE_DIR / f"{h}.html"


def fetch_page(url: str, cache_filename: str | None = None) -> tuple[str, bool]:
    """Fetch an HTML page politely with caching, delay, timeout, and custom user-agent.

    Returns (html_content, was_cache_hit).
    """
    global _last_request_time
    cache_path = _url_to_cache_path(url, cache_filename)

    # 1. Check cache
    if cache_path.exists():
        html = cache_path.read_text(encoding="utf-8")
        stats["cache_hits"] += 1
        print(f"CACHE HIT: {url} ({len(html)} bytes) -> {cache_path}")
        return html, True

    # 2. Polite delay (at least 0.5 seconds between real network requests)
    now = time.time()
    elapsed = now - _last_request_time
    if elapsed < DELAY_SECONDS:
        time.sleep(DELAY_SECONDS - elapsed)

    # 3. Request over network
    headers = {"User-Agent": USER_AGENT}
    try:
        resp = requests.get(url, headers=headers, timeout=TIMEOUT_SECONDS)
        _last_request_time = time.time()
        if resp.status_code != 200:
            stats["failed_pages"] += 1
            stats["errors"].append(f"HTTP {resp.status_code} for {url}")
            raise RuntimeError(f"Failed to fetch {url}: HTTP {resp.status_code}")
        
        html = resp.text
        cache_path.write_text(html, encoding="utf-8")
        stats["pages_fetched"] += 1
        print(f"FETCH: {url} ({len(html)} bytes, status 200) -> saved to {cache_path}")
        return html, False
    except requests.RequestException as e:
        stats["failed_pages"] += 1
        stats["errors"].append(f"Network error for {url}: {str(e)}")
        raise RuntimeError(f"Request failed for {url}: {e}")
