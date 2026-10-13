import json
from pathlib import Path

from crawler import discover_book_urls
from extractor import extract_raw_book_record
from models import BookRecord, normalize_record

OUTPUT_DIR = Path("output")


def process_records() -> tuple[list[dict], list[dict]]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    books, pages = discover_book_urls()

    validated_books: list[dict] = []
    seen_urls: set[str] = set()
    errors: list[dict] = []

    for url, source in books:
        if url in seen_urls:
            continue
        seen_urls.add(url)

        try:
            raw = extract_raw_book_record(url, source)
            normalized = normalize_record(raw)
            # Validate with Pydantic
            valid_model = BookRecord(**normalized)
            validated_books.append(valid_model.model_dump())
        except Exception as e:
            errors.append({"url": url, "error": str(e)})

    # Idempotent write to output/books.json
    (OUTPUT_DIR / "books.json").write_text(
        json.dumps(validated_books, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    if errors:
        (OUTPUT_DIR / "errors.json").write_text(
            json.dumps(errors, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

    return validated_books, errors


def main():
    books, errors = process_records()
    print(f"Validated books count: {len(books)}")
    print(f"Errors count: {len(errors)}")
    # Check first record price_gbp
    if books:
        print(f"Sample price_gbp: {books[0]['price_gbp']} (type: {type(books[0]['price_gbp'])})")
        print(f"Sample product_url: {books[0]['product_url']}")


if __name__ == "__main__":
    main()
