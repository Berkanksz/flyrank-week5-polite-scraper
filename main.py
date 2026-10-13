from fetcher import fetch_page

BASE_URL = "https://books.toscrape.com/catalogue/page-1.html"


def main():
    print("Stage 1 test:")
    html, hit = fetch_page(BASE_URL, cache_filename="catalogue-page-1.html")
    print(f"Result: {len(html)} characters, cached: {hit}")


if __name__ == "__main__":
    main()
