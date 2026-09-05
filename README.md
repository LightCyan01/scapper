# The Polite Scraper

A small web scraping project built with Python for the FlyRank Backend Internship.

The goal of this project is to scrape book information from **Books to Scrape** while following polite scraping practices such as limiting the scope, using timeouts, caching requests, and avoiding unnecessary traffic.

## Target Classification

### Target

The target website is **Books to Scrape**:

https://books.toscrape.com/

Books to Scrape is a public practice sandbox designed for learning and testing web scraping.

### Scope

This scraper will only process the **first 3 catalogue pages** and the book detail pages discovered from those catalogue pages.

The expected result is 60 unique books.

### Data Collected

For each book, the scraper will eventually collect:

- Title
- Product URL
- Price
- Availability
- Rating
- Description
- Source page
- Fetch time

The cleaned version of the data will also include a numeric price value.