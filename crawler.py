from urllib.parse import urljoin
from bs4 import BeautifulSoup

from fetcher import fetch_page

START_URL = "https://books.toscrape.com/catalogue/page-1.html"
MAX_CATALOGUE_PAGES = 3


def discover_book_urls(start_url: str = START_URL, max_pages: int = MAX_CATALOGUE_PAGES) -> tuple[list[tuple[str, str]], int]:
    """Crawl up to max_pages catalogue pages following the 'next' button.

    Returns a list of (book_absolute_url, source_catalogue_page_url) and the number of catalogue pages crawled.
    """
    discovered_books: list[tuple[str, str]] = []
    seen_urls: set[str] = set()
    current_url = start_url
    catalogue_pages_crawled = 0

    while current_url and catalogue_pages_crawled < max_pages:
        page_num = catalogue_pages_crawled + 1
        html, _ = fetch_page(current_url, cache_filename=f"catalogue-page-{page_num}.html")
        catalogue_pages_crawled += 1

        soup = BeautifulSoup(html, "html.parser")

        # Find all book article containers
        for article in soup.select("article.product_pod"):
            link_tag = article.select_one("h3 > a")
            if link_tag and link_tag.get("href"):
                relative_url = link_tag["href"]
                abs_url = urljoin(current_url, relative_url)
                if abs_url not in seen_urls:
                    seen_urls.add(abs_url)
                    discovered_books.append((abs_url, current_url))

        # Follow next button
        next_button = soup.select_one("li.next > a")
        if next_button and next_button.get("href"):
            current_url = urljoin(current_url, next_button["href"])
        else:
            break

    return discovered_books, catalogue_pages_crawled
