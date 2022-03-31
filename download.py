from ast import parse
import re
import requests
from bs4 import BeautifulSoup

base_url = "https://letterboxd.com"

imdb_pattern = re.compile(r"http:\/\/www\.imdb\.com/title/(tt\d{7})/maindetails")

def _find_links_in_list(list_link):
    """Finds all the links from a list"""
    response = requests.get(list_link)
    page = response.text
    soup = BeautifulSoup(page, "html.parser")
    table = soup.find("ul", class_="poster-list")
    items = table.find_all("li")
    movie_links = (f"{base_url}{li.div.get('data-film-slug')}" for li in items)
    yield from movie_links
    if next_url_tag := soup.find("a", class_="next"):
        next_url = f"{base_url}{next_url_tag.get('href')}"
        yield from _find_links_in_list(next_url)


def _parse_link(movie_link):
    response = requests.get(movie_link)
    page = response.text
    soup = BeautifulSoup(page, "html.parser")
    imdb_tag = soup.find("a", {"data-track-action": "IMDb"})
    imdb_url = imdb_tag.get("href")
    imdb_id = re.match(imdb_pattern, imdb_url).group(1)
    return imdb_id


def download_list(list_link):
    movie_links = _find_links_in_list(list_link)
    return (_parse_link(movie_id) for movie_id in movie_links)

    


if __name__ == "__main__":
    print(list(download_list("https://letterboxd.com/testuser_py/likes/films/")))
