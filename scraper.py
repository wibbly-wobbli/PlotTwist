import requests
from bs4 import BeautifulSoup
import urllib.parse

BASE_URL = "https://www.isfdb.org"

def search_isfdb(title):
    search_url = f"{BASE_URL}/cgi-bin/title.cgi?title={urllib.parse.quote_plus(title)}"
    response = requests.get(search_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # If it redirects to a specific title, parse directly
    if "Title Summary" in soup.title.text:
        return parse_title_page(soup)

    # Otherwise, it's a search results page
    results = soup.select('ul li a')
    if not results:
        print("No results found.")
        return None

    first_result = results[0]
    href = first_result.get('href')
    title_page = requests.get(BASE_URL + href)
    return parse_title_page(BeautifulSoup(title_page.text, 'html.parser'))

def parse_title_page(soup):
    data = {}

    data['title'] = soup.find("h1").text.strip()
    
    # Author
    author_tag = soup.find("b", string="Author:")
    if author_tag:
        data['author'] = author_tag.find_next("a").text

    # Year
    year_tag = soup.find("b", string="Year:")
    if year_tag:
        data['year'] = year_tag.next_sibling.strip()

    # Series (optional)
    series_tag = soup.find("b", string="Series:")
    if series_tag:
        data['series'] = series_tag.find_next("a").text

    # Summary (if available)
    synopsis = soup.find("div", class_="note")
    if synopsis:
        data['summary'] = synopsis.text.strip()

    return data
