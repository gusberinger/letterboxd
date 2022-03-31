import re
import requests
from bs4 import BeautifulSoup

base_url = "https://letterboxd.com"

imdb_pattern = re.compile(r"http:\/\/www\.imdb\.com/title/(tt\d{7})/maindetails")

def find_links_in_list(link):
    """Finds all the links from a list"""
    response = requests.get(link)
    page = response.text
    soup = BeautifulSoup(page, "html.parser")
    table = soup.find("ul", class_="poster-list")
    items = table.find_all("li")
    links = (f"{base_url}{li.div.get('data-film-slug')}" for li in items)
    yield from links
    if next_url_tag := soup.find("a", class_="next"):
        next_url = f"{base_url}{next_url_tag.get('href')}"
        yield from find_links_in_list(next_url)


def parse_link(link):
    response = requests.get(link)
    page = response.text
    soup = BeautifulSoup(page, "html.parser")
    imdb_tag = soup.find("a", {"data-track-action": "IMDb"})
    imdb_url = imdb_tag.get("href")
    imdb_id = re.match(imdb_pattern, imdb_url).group(1)
    return imdb_id

    


if __name__ == "__main__":
    for links in tqdm(find_links_in_list())
