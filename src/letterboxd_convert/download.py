from functools import cache
import itertools
import re
import time
from typing import Iterable, Optional, List
import requests
import httpx
import asyncio
from bs4 import BeautifulSoup

base_url = "https://letterboxd.com"
imdb_pattern = re.compile(r"http:\/\/www\.imdb\.com/title/(tt\d{7,8})/maindetails")


def _find_pages_in_list(
    list_url: str, limit: float = float("inf"), acc: int = 0, rate: float = 1
) -> Iterable[str]:
    """Finds all the links from a list"""
    response = requests.get(list_url)
    soup = BeautifulSoup(response.text, "html.parser")
    items = soup.find("ul", class_="poster-list").find_all("li")
    movie_links = (f"{base_url}{li.div.get('data-film-slug')}" for li in items)
    yield from movie_links
    next_url_tag = soup.find("a", class_="next")
    if next_url_tag and acc < limit:
        next_url = f"{base_url}{next_url_tag.get('href')}"
        time.sleep(rate)
        yield from _find_pages_in_list(next_url, limit, acc + len(items))


async def download_pages(page_urls: List[str]):
    async with httpx.AsyncClient() as client:
        pages = (client.get(url) for url in page_urls)
        responses = await asyncio.gather(*pages)
    return responses

# async def download_pages(page_urls):
#     print(page_urls)
#     async with httpx.AsyncClient() as client:
#         response = await client.get('https://www.example.com/')
#         # print(response.text)
#     return response


@cache
def _parse_page(page_response: str) -> str:
    page = page_response.text
    soup = BeautifulSoup(page, "html.parser")
    imdb_tag = soup.find("a", {"data-track-action": "IMDb"})
    imdb_url = imdb_tag.get("href")
    imdb_id_match = re.match(imdb_pattern, imdb_url)
    assert imdb_id_match is not None
    imdb_id = imdb_id_match.group(1)
    return imdb_id


def download_list(
    list_url: str, limit: Optional[int] = None, rate: int = 1
) -> Iterable[str]:
    """
    Parameters
    ___
    list_url:
        The url to the letterboxd.com list.
    limit:
        The maximum number of movies to fetch from the list.
    rate:
        The wait time in seconds between every 20 movies.
    """
    if limit is None:
        numerical_limit = float("inf")
    else:
        numerical_limit = limit
    rate = max(rate, 1)
    movie_links = _find_pages_in_list(list_url, limit=numerical_limit, rate=rate)
    pages = asyncio.run(download_pages(movie_links))
    imdb_ids = (_parse_page(page) for page in pages)
    return itertools.islice(imdb_ids, limit)
