import json
import time
from datetime import datetime, timezone
from pathlib import Path

from crawler import discover_book_urls
from extractor import extract_raw_book_record
from fetcher import stats
from models import BookRecord, normalize_record

OUTPUT_DIR = Path("output")


def run_pipeline(include_fake_failure: bool = False) -> tuple[list[dict], dict]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    start_time = datetime.now(timezone.utc)
    t0 = time.time()

    # Reset stats
    stats["pages_fetched"] = 0
    stats["cache_hits"] = 0
    stats["failed_pages"] = 0
    stats["errors"] = []

    # 1. Discover catalogue pages
    books, pages_count = discover_book_urls()

    # Optional Stage 5 test: add one deliberately broken fake URL
    if include_fake_failure:
        fake_url = "https://books.toscrape.com/catalogue/non_existent_fake_book_9999/index.html"
        books.append((fake_url, "https://books.toscrape.com/catalogue/page-1.html"))

    validated_books: list[dict] = []
    seen_urls: set[str] = set()
    errors: list[dict] = []

    # 2. Extract and validate each book independently
    for url, source in books:
        if url in seen_urls:
            continue
        seen_urls.add(url)

        try:
            raw = extract_raw_book_record(url, source)
            normalized = normalize_record(raw)
            valid_model = BookRecord(**normalized)
            validated_books.append(valid_model.model_dump())
        except Exception as e:
            # One bad page must not kill the run
            errors.append({"url": url, "error": str(e)})

    # 3. Store valid books (idempotent write)
    (OUTPUT_DIR / "books.json").write_text(
        json.dumps(validated_books, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    if errors:
        (OUTPUT_DIR / "errors.json").write_text(
            json.dumps(errors, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
    else:
        # Clean up errors.json if none
        err_file = OUTPUT_DIR / "errors.json"
        if err_file.exists():
            err_file.unlink()

    duration_seconds = round(time.time() - t0, 3)

    # 4. Generate honest run report
    report = {
        "start_time": start_time.isoformat().replace("+00:00", "Z"),
        "duration_seconds": duration_seconds,
        "catalogue_pages": pages_count,
        "discovered_urls": len(books),
        "unique_urls": len(seen_urls),
        "pages_fetched": stats["pages_fetched"],
        "cache_hits": stats["cache_hits"],
        "valid_records": len(validated_books),
        "invalid_records": len(errors),
        "failed_pages": stats["failed_pages"],
        "errors": stats["errors"]
    }

    (OUTPUT_DIR / "run-report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    return validated_books, report


def main():
    import sys
    with_fake = "--test-failure" in sys.argv
    print(f"Starting scraper pipeline (test_failure={with_fake})...")
    books, report = run_pipeline(include_fake_failure=with_fake)
    print(f"Run completed in {report['duration_seconds']}s")
    print(f"Valid records: {report['valid_records']}")
    print(f"Failed pages: {report['failed_pages']}")
    print("\n--- run-report.json ---")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
