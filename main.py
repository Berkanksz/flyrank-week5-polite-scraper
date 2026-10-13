from crawler import discover_book_urls


def main():
    books, pages = discover_book_urls()
    print(f"catalogue_pages={pages}, discovered={len(books)}, unique_urls={len(set(b[0] for b in books))}")


if __name__ == "__main__":
    main()
