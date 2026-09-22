import os
import time
import json
import requests

from datetime import datetime, timezone
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pydantic import BaseModel, ValidationError


headers = {
    "User-Agent": "FlyRankInternship A9/1.0 (+https://github.com/LightCyan01/scapper)"
}

stats = {
    "pages_fetched": 0,
    "cache_hits": 0
}


class Book(BaseModel):
    title: str
    product_url: str
    price_text: str
    price_gbp: float
    availability_text: str
    rating_text: str
    description: str | None
    source_page: str
    fetched_at: str


def fetch_page(url, cache_file):
    os.makedirs("cache", exist_ok=True)

    if os.path.exists(cache_file):
        print("CACHE HIT")
        stats["cache_hits"] += 1

        with open(cache_file, "r", encoding="utf-8") as file:
            return file.read()

    for attempt in range(2):
        print("FETCH")
        time.sleep(0.5)

        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=5
            )

        except requests.exceptions.Timeout:
            print("Request timed out")

            if attempt == 0:
                print("Retrying once...")
                time.sleep(1)
                continue

            return None

        if response.status_code == 200:
            response.encoding = "utf-8"
            html = response.text

            stats["pages_fetched"] += 1

            with open(cache_file, "w", encoding="utf-8") as file:
                file.write(html)

            return html

        if 500 <= response.status_code < 600 and attempt == 0:
            print(f"Server error {response.status_code}")
            print("Retrying once...")
            time.sleep(1)
            continue
        print(f"Request failed {response.status_code}")
        return None

    return None


def main():
    start_time = datetime.now(timezone.utc)
    start_clock = time.time()

    url = "https://books.toscrape.com/catalogue/page-1.html"

    discovered_books = []
    catalogue_pages = 0
    failed_pages = []

    while catalogue_pages < 3:
        page_number = catalogue_pages + 1
        cache_file = f"cache/catalogue-page-{page_number}.html"

        html = fetch_page(url, cache_file)

        if html is None:
            failed_pages.append(url)
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

    unique_books = {}

    for book in discovered_books:
        unique_books[book["product_url"]] = book

    books = list(unique_books.values())

    print(f"catalogue_pages={catalogue_pages}")
    print(f"discovered={len(discovered_books)}")
    print(f"unique_urls={len(books)}")

    valid_records = {}
    errors = []

    for index, book in enumerate(books, start=1):
        product_url = book["product_url"]
        source_page = book["source_page"]

        cache_file = f"cache/book-{index}.html"

        html = fetch_page(product_url, cache_file)

        if html is None:
            failed_pages.append(product_url)
            print(f"SKIPPED: {product_url}")
            continue

        soup = BeautifulSoup(html, "html.parser")

        title = soup.select_one(
            "div.product_main h1"
        ).get_text(strip=True)

        price_text = soup.select_one(
            "div.product_main p.price_color"
        ).get_text(strip=True)

        price_gbp = float(
            price_text.replace("£", "")
        )

        availability_text = soup.select_one(
            "div.product_main p.instock.availability"
        ).get_text(" ", strip=True)

        rating = soup.select_one("p.star-rating")

        rating_text = ""

        for class_name in rating.get("class", []):
            if class_name != "star-rating":
                rating_text = class_name

        description = None

        description_heading = soup.select_one(
            "#product_description"
        )

        if description_heading is not None:
            description_paragraph = (
                description_heading.find_next_sibling("p")
            )

            if description_paragraph is not None:
                description = description_paragraph.get_text(
                    strip=True
                )

        fetched_at = datetime.fromtimestamp(
            os.path.getmtime(cache_file),
            timezone.utc
        ).isoformat().replace("+00:00", "Z")

        raw_record = {
            "title": title,
            "product_url": product_url,
            "price_text": price_text,
            "price_gbp": price_gbp,
            "availability_text": availability_text,
            "rating_text": rating_text,
            "description": description,
            "source_page": source_page,
            "fetched_at": fetched_at
        }

        try:
            validated = Book(**raw_record)

            valid_records[product_url] = validated.model_dump()

        except ValidationError as error:
            errors.append({
                "record": raw_record,
                "reason": str(error)
            })

    os.makedirs("output", exist_ok=True)

    with open(
        "output/books.json",
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            list(valid_records.values()),
            file,
            indent=2,
            ensure_ascii=False
        )

    with open(
        "output/errors.json",
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            errors,
            file,
            indent=2,
            ensure_ascii=False
        )

    duration = time.time() - start_clock

    run_report = {
        "start_time": start_time.isoformat().replace("+00:00", "Z"),
        "duration_seconds": round(duration, 2),
        "pages_fetched": stats["pages_fetched"],
        "cache_hits": stats["cache_hits"],
        "valid_records": len(valid_records),
        "invalid_records": len(errors),
        "failed_pages": len(failed_pages)
    }

    with open(
        "output/run-report.json",
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            run_report,
            file,
            indent=2
        )

    print()
    print("RUN REPORT")
    print(json.dumps(run_report, indent=2))


if __name__ == "__main__":
    main()