import os
import time
import json
import requests

from datetime import datetime, timezone
from bs4 import BeautifulSoup
from urllib.parse import urljoin


headers = {
    "User-Agent": "FlyRankInternship A9/1.0 (+https://github.com/LightCyan01/scapper)"
}


def fetch_page(url, cache_file):
    os.makedirs("cache", exist_ok=True)

    if os.path.exists(cache_file):
        print("CACHE HIT")

        with open(cache_file, "r", encoding="utf-8") as file:
            return file.read()

    print("FETCH")
    time.sleep(0.5)

    response = requests.get(
        url,
        headers=headers,
        timeout=5
    )

    if response.status_code != 200:
        print(f"Request failed {response.status_code}")
        return None

    html = response.text

    with open(cache_file, "w", encoding="utf-8") as file:
        file.write(html)

    return html


def main():
    url = "https://books.toscrape.com/catalogue/page-1.html"

    discovered_books = []
    catalogue_pages = 0

    # Find the books from the first 3 catalogue pages
    while catalogue_pages < 3:
        page_number = catalogue_pages + 1
        cache_file = f"cache/catalogue-page-{page_number}.html"

        html = fetch_page(url, cache_file)

        if html is None:
            break

        catalogue_pages += 1

        soup = BeautifulSoup(html, "html.parser")

        books = soup.select("article.product_pod h3 a")

        for book in books:
            href = book["href"]
            full_url = urljoin(url, href)

            discovered_books.append({
                "product_url": full_url,
                "source_page": url
            })

        next_button = soup.select_one("li.next a")

        if next_button is None:
            break

        next_href = next_button["href"]
        url = urljoin(url, next_href)

    # Remove duplicate book URLs
    unique_books = {}

    for book in discovered_books:
        unique_books[book["product_url"]] = book

    books = list(unique_books.values())

    print(f"catalogue_pages={catalogue_pages}")
    print(f"discovered={len(discovered_books)}")
    print(f"unique_urls={len(books)}")

    # Visit all 60 book detail pages
    records = []

    for index, book in enumerate(books, start=1):
        product_url = book["product_url"]
        source_page = book["source_page"]

        cache_file = f"cache/book-{index}.html"

        html = fetch_page(product_url, cache_file)

        if html is None:
            continue

        soup = BeautifulSoup(html, "html.parser")

        title = soup.select_one("div.product_main h1").get_text(strip=True)

        price_text = soup.select_one(
            "div.product_main p.price_color"
        ).get_text(strip=True)

        availability_text = soup.select_one(
            "div.product_main p.instock.availability"
        ).get_text(" ", strip=True)

        rating = soup.select_one("p.star-rating")

        rating_text = None

        if rating is not None:
            for class_name in rating.get("class", []):
                if class_name != "star-rating":
                    rating_text = class_name

        description = None

        description_heading = soup.select_one("#product_description")

        if description_heading is not None:
            description_paragraph = description_heading.find_next_sibling("p")

            if description_paragraph is not None:
                description = description_paragraph.get_text(strip=True)

        # Use the cache file time as the time this page was fetched
        fetched_at = datetime.fromtimestamp(
            os.path.getmtime(cache_file),
            timezone.utc
        ).isoformat().replace("+00:00", "Z")

        record = {
            "title": title,
            "product_url": product_url,
            "price_text": price_text,
            "availability_text": availability_text,
            "rating_text": rating_text,
            "description": description,
            "source_page": source_page,
            "fetched_at": fetched_at
        }

        records.append(record)

    print()
    print("ONE RAW RECORD:")
    print(json.dumps(records[0], indent=2, ensure_ascii=False))

    print()
    print(f"detail_pages={len(records)}")


if __name__ == "__main__":
    main()