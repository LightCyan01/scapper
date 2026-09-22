# The Polite Scraper

A Python scraper built for the FlyRank Backend Internship.

The script reads the first three catalogue pages from Books to Scrape, finds the 60 books listed on those pages, visits each book page, validates the scraped data with Pydantic, and saves the results as JSON.

## Target classification

### Target

https://books.toscrape.com/

Books to Scrape is a public sandbox created for practicing web scraping.

### Scope

This scraper only processes the first three catalogue pages and the book pages found on them.

That gives a total of 60 books.

### Data collected

Each saved book record contains:

| Field               | Type           | Description                             |
| ------------------- | -------------- | --------------------------------------- |
| `title`             | string         | Book title                              |
| `product_url`       | string         | Absolute URL of the book page           |
| `price_text`        | string         | Original price text                     |
| `price_gbp`         | float          | Price converted to a number             |
| `availability_text` | string         | Availability shown on the page          |
| `rating_text`       | string         | Star rating                             |
| `description`       | string or null | Book description                        |
| `source_page`       | string         | Catalogue page where the book was found |
| `fetched_at`        | string         | Time the page was fetched               |

### robots.txt

I requested:

```text
https://books.toscrape.com/robots.txt
```

The server returned:

```text
404 Not Found
```

No robots file was found.

A missing `robots.txt` file is not permission by itself. I am using Books to Scrape because it is specifically provided as a practice sandbox.

I will not reuse this code on another site without checking its rules and terms first.

## Setup

This project uses Python 3.10+ and `uv`.

The main dependencies are Requests, Beautiful Soup, and Pydantic.

Clone the repository:

```bash
git clone https://github.com/LightCyan01/scapper.git
cd scapper
```

Install the dependencies:

```bash
uv sync
```

Run the scraper:

```bash
uv run src/main.py
```

## Output

A completed run creates:

```text
output/
├── books.json
├── errors.json
└── run-report.json
```

`books.json` contains the validated book records.

`errors.json` contains records that failed validation and the reason for each failure.

`run-report.json` contains the run time, fetch count, cache hits, valid records, invalid records, and failed pages.

## Request handling and caching

Every request sent to the site uses:

- an identifying User-Agent
- a 5 second timeout
- at least a 0.5 second delay before a real request
- an HTTP status check

Successful HTML responses are saved in the local `cache/` directory.

If a cached page already exists, the scraper reads that file instead of requesting the page again.

Timeouts and `5xx` server errors are retried once. Responses such as `403` and `404` are not retried.

The `cache/` directory is excluded from Git.

## Validation

The scraper keeps both the original price text and a numeric version.

For example:

```json
{
  "price_text": "£51.77",
  "price_gbp": 51.77
}
```

Pydantic validates each finished record before it is stored.

Records that fail validation are written to `errors.json` instead of `books.json`.

The product URL is used as the unique identity for a book, so running the scraper again does not add duplicate records.

## Run report

```json
{
  "start_time": "2026-09-22T11:01:59.192095Z",
  "duration_seconds": 46.9,
  "pages_fetched": 63,
  "cache_hits": 0,
  "valid_records": 60,
  "invalid_records": 0,
  "failed_pages": 0
}
```

## Why no browser is needed

The book data needed for this assignment is already present in the HTML returned by the server.

Because of that, a browser automation tool such as Playwright is unnecessary for the main scraper and would add extra processing and memory use.

## Ethics

I would use an official API instead of scraping when one is available.

I would not use scraping to bypass logins, paywalls, access restrictions, or blocks. I would also only collect the information needed for the task.

## Result

A normal run produces 60 unique validated book records.
