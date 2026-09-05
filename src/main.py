import requests

def main():
    url = "https://books.toscrape.com/robots.txt"
    response = requests.get(url)
    print(response.status_code)
    print(response.text)

if __name__ == "__main__":
    main()
