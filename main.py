from crawler import discover_book_urls
from extractor import extract_raw_book_record


def main():
    books, pages = discover_book_urls()
    print(f"Discover complete: {len(books)} books across {pages} pages.")

    raw_records = []
    for url, source in books:
        record = extract_raw_book_record(url, source)
        raw_records.append(record)

    print(f"\ndetail_pages={len(raw_records)}")
    print("\nSample complete raw record:")
    import json
    print(json.dumps(raw_records[0], indent=2))


if __name__ == "__main__":
    main()
