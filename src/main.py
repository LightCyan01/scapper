import os
import requests

def main():
    url = "https://books.toscrape.com/catalogue/page-1.html"
    cache_file = "cache/catalogue-page-1.html"
    
    headers = {
        "User-Agent": "FlyRankInternShip"
    }
    
    os.makedirs("cache", exist_ok=True)
    
    if os.path.exists(cache_file):
        print("CACHE HIT")
        
        with open(cache_file, "r", encoding="utf-8") as file:
            html = file.read()
    else:
        print ("FETCH")
        
        response = requests.get(
            url,
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            html = response.text
            
            with open(cache_file, "w", encoding="utf-8") as file:
                file.write(html)
        else:
            print("Request failed", response.status_code)
            return
    
    print(f"Size: {len(html)}")
    
if __name__ == "__main__":
    main()
