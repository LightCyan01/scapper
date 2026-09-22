import os
import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin

headers = {
        "User-Agent": "FlyRankInternship A9/1.0 https://github.com/LightCyan01/scapper"
    }

def fetch_page(url, cache_file):
    os.makedirs("cache", exist_ok=True)
    
    if os.path.exists(cache_file):
        print("CACHE HIT")
        
        with open(cache_file, "r", encoding="utf-8") as file:
            html = file.read()
            
        return html
            
    print ("FETCH")
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
    book_urls = []
    catalogue_pages = 0

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

            book_urls.append(full_url)

        next_button = soup.select_one("li.next a")

        if next_button is None:
            break

        next_href = next_button["href"]
        url = urljoin(url, next_href)

    unique_urls = list(set(book_urls))

    print(f"catalogue_pages={catalogue_pages}")
    print(f"discovered={len(book_urls)}")
    print(f"unique_urls={len(unique_urls)}")
    

if __name__ == "__main__":
    main()
