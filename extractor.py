from datetime import datetime, timezone
import re
from bs4 import BeautifulSoup

from fetcher import fetch_page


def extract_raw_book_record(product_url: str, source_page: str) -> dict:
    """Fetch and extract raw fields from a book detail page.

    Keeps the exact 8 keys required by Stage 3:
    - title
    - product_url
    - price_text
    - availability_text
    - rating_text
    - description
    - source_page
    - fetched_at
    """
    html, _ = fetch_page(product_url)
    fetched_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    soup = BeautifulSoup(html, "html.parser")
    product_main = soup.select_one("div.product_main")
    if not product_main:
        raise ValueError(f"Could not find product_main in {product_url}")

    # Title
    title_tag = product_main.select_one("h1")
    title = title_tag.get_text(strip=True) if title_tag else "Unknown Title"

    # Price
    price_tag = product_main.select_one("p.price_color")
    price_text = price_tag.get_text(strip=True) if price_tag else "£0.00"

    # Availability
    avail_tag = product_main.select_one("p.availability")
    availability_text = " ".join(avail_tag.get_text(strip=True).split()) if avail_tag else ""

    # Rating
    star_tag = product_main.select_one("p.star-rating")
    rating_text = "None"
    if star_tag:
        classes = star_tag.get("class", [])
        for c in classes:
            if c != "star-rating":
                rating_text = c
                break

    # Description (optional, None if missing)
    description = None
    sub_header = soup.select_one("#product_description")
    if sub_header:
        p_desc = sub_header.find_next_sibling("p")
        if p_desc:
            description = p_desc.get_text(strip=True)

    return {
        "title": title,
        "product_url": product_url,
        "price_text": price_text,
        "availability_text": availability_text,
        "rating_text": rating_text,
        "description": description,
        "source_page": source_page,
        "fetched_at": fetched_at
    }
