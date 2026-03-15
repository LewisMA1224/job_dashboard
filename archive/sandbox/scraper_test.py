import csv
import requests
from bs4 import BeautifulSoup

url = "https://quotes.toscrape.com/"

response = requests.get(url, timeout=10)
response.raise_for_status()

soup = BeautifulSoup(response.text, "lxml")

quote_blocks = soup.find_all("div", class_="quote")

rows = []

for block in quote_blocks:
    text = block.find("span", class_="text").get_text(strip=True)
    author = block.find("small", class_="author").get_text(strip=True)
    rows.append([text, author])

with open("quotes.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["quote", "author"])
    writer.writerows(rows)

print(f"Saved {len(rows)} quotes to quotes.csv")
