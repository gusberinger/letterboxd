from functools import cache
import re
import itertools
from typing import Iterable, Optional
import httpx
import asyncio
from bs4 import BeautifulSoup, Tag
from .database import DBConnection

base_url = "https://letterboxd.com"
imdb_pattern = re.compile(r"http:\/\/www\.imdb\.com/title/(tt\d{7,8})/maindetails")


class MissingIMDbPage(Exception):
    """IMDb does not contain this movie."""


async def download_pages(page_urls: Iterable[str]) -> Iterable[httpx.Response]:
    async with httpx.AsyncClient() as client:
        pages = (client.get(url) for url in page_urls)
        responses = await asyncio.gather(*pages)
    return responses


def _find_pages_in_list(
    list_url: str, limit: float = float("inf"), acc: int = 0
) -> Iterable[str]:
    """Finds all the links from a list"""
    response = httpx.get(list_url)
    soup = BeautifulSoup(response.text, "html.parser")
    poster_table = soup.find("ul", class_="poster-list")
    assert isinstance(poster_table, Tag)
    items = poster_table.find_all("li")
    movie_links = (f"{base_url}{li.div.get('data-film-slug')}" for li in items)
    yield from movie_links
    next_url_tag = soup.find("a", class_="next")
    if next_url_tag and acc < limit:
        assert isinstance(next_url_tag, Tag)
        next_url = f"{base_url}{next_url_tag.get('href')}"
        yield from _find_pages_in_list(next_url, limit, acc + len(items))


def _parse_page(page_response: httpx.Response) -> str:
    page = page_response.text
    soup = BeautifulSoup(page, "html.parser")
    imdb_tag = soup.find("a", {"data-track-action": "IMDb"})
    if imdb_tag is None:
        raise MissingIMDbPage()
    assert isinstance(imdb_tag, Tag)
    imdb_url = imdb_tag.get("href")
    assert isinstance(imdb_url, str)
    imdb_id_match = re.match(imdb_pattern, imdb_url)
    assert imdb_id_match is not None
    imdb_id = imdb_id_match.group(1)
    return imdb_id

def get_tconst(url, db: 'DBConnection'):
    try:
        return db.get_tconst(url)
    except KeyError:
        return _parse_page(url)


def download_list(
    list_url: str, limit: Optional[int] = None, rate: int = 1, strict: bool = False
) -> Iterable[str]:
    """
    Parameters
    ___
    list_url:
        The url to the letterboxd.com list.
    limit:
        The maximum number of movies to fetch from the list.
    """
    if limit is None:
        numerical_limit = float("inf")
    else:
        numerical_limit = limit
    movie_links = _find_pages_in_list(list_url, limit=numerical_limit)
    pages = asyncio.run(download_pages(movie_links))
    db = DBConnection()
    for page in itertools.islice(pages, limit):
        try:
            tconst = get_tconst(page, db)
            yield tconst
        except MissingIMDbPage as e:
            if strict:
                raise e
