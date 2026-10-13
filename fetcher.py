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


def _make_request(url: str) -> tuple[int, str]:
    """Execute a single HTTP request respecting polite delay."""
    global _last_request_time
    now = time.time()
    elapsed = now - _last_request_time
    if elapsed < DELAY_SECONDS:
        time.sleep(DELAY_SECONDS - elapsed)

    headers = {"User-Agent": USER_AGENT}
    resp = requests.get(url, headers=headers, timeout=TIMEOUT_SECONDS)
    _last_request_time = time.time()
    return resp.status_code, resp.text


def fetch_page(url: str, cache_filename: str | None = None) -> tuple[str, bool]:
    """Fetch an HTML page politely with caching, retry logic on 5xx/timeout, and politeness."""
    cache_path = _url_to_cache_path(url, cache_filename)

    # 1. Check cache
    if cache_path.exists():
        html = cache_path.read_text(encoding="utf-8")
        stats["cache_hits"] += 1
        return html, True

    # 2. Attempt fetch with single retry on server error (5xx) or timeout
    attempts = 0
    max_attempts = 2

    while attempts < max_attempts:
        attempts += 1
        try:
            status_code, html = _make_request(url)

            if status_code == 200:
                cache_path.write_text(html, encoding="utf-8")
                stats["pages_fetched"] += 1
                return html, False

            # Do not retry 404 (Not Found) or 403 (Forbidden)
            if status_code in (404, 403):
                stats["failed_pages"] += 1
                stats["errors"].append(f"HTTP {status_code} for {url} (permanent, no retry)")
                raise RuntimeError(f"HTTP {status_code} for {url}")

            # 5xx Server error -> wait and retry once
            if status_code >= 500 and attempts < max_attempts:
                time.sleep(1.0)
                continue

            stats["failed_pages"] += 1
            stats["errors"].append(f"HTTP {status_code} for {url}")
            raise RuntimeError(f"HTTP {status_code} for {url}")

        except (requests.Timeout, requests.ConnectionError) as e:
            if attempts < max_attempts:
                time.sleep(1.0)
                continue
            stats["failed_pages"] += 1
            stats["errors"].append(f"Network error for {url}: {e}")
            raise RuntimeError(f"Request failed for {url}: {e}")
        except requests.RequestException as e:
            stats["failed_pages"] += 1
            stats["errors"].append(f"Request error for {url}: {e}")
            raise RuntimeError(f"Request failed for {url}: {e}")
