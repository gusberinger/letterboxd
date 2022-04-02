from functools import cache
import itertools
import re
import time
from typing import Iterable, Optional
import requests
from bs4 import BeautifulSoup

base_url = "https://letterboxd.com"
imdb_pattern = re.compile(
    r"http:\/\/www\.imdb\.com/title/(tt\d{7,8})/maindetails"
)


def _find_links_in_list(list_link: str, limit: float = float("inf"),
                        acc: int = 0, rate: float = 1) -> Iterable[str]:
    """Finds all the links from a list"""
    response = requests.get(list_link)
    soup = BeautifulSoup(response.text, "html.parser")
    items = soup.find("ul", class_="poster-list").find_all("li")
    movie_links = (f"{base_url}{li.div.get('data-film-slug')}" for li in items)
    yield from movie_links
    next_url_tag = soup.find("a", class_="next")
    if next_url_tag and acc < limit:
        next_url = f"{base_url}{next_url_tag.get('href')}"
        time.sleep(rate)
        yield from _find_links_in_list(next_url, limit, acc + len(items))


@cache
def _parse_link(movie_link: str) -> str:
    response = requests.get(movie_link)
    page = response.text
    soup = BeautifulSoup(page, "html.parser")
    imdb_tag = soup.find("a", {"data-track-action": "IMDb"})
    imdb_url = imdb_tag.get("href")
    imdb_id_match = re.match(imdb_pattern, imdb_url)
    assert imdb_id_match is not None
    imdb_id = imdb_id_match.group(1)
    return imdb_id


def download_list(list_link: str,
                  limit: Optional[int] = None, rate: int = 1) -> Iterable[str]:
    if limit is None:
        numerical_limit = float("inf")
    else:
        numerical_limit = limit
    rate = max(rate, 1)
    movie_links = _find_links_in_list(
        list_link,
        limit=numerical_limit,
        rate=rate)
    imdb_ids = (_parse_link(movie) for movie in movie_links)
    return itertools.islice(imdb_ids, limit)
