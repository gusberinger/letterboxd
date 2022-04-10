import asyncio
import re
import itertools
from typing import Iterable, List, Optional
import httpx
from bs4 import BeautifulSoup, Tag

from letterboxd_convert.database import DBConnection

base_url = "https://letterboxd.com"
imdb_pattern = re.compile(r"http:\/\/www\.imdb\.com/title/(tt\d{7,8})/maindetails")


class MissingIMDbPage(Exception):
    """IMDb does not contain this movie."""


async def async_download_pages(page_urls: Iterable[str]) -> Iterable[httpx.Response]:
    async with httpx.AsyncClient() as client:
        pages = (client.get(url) for url in page_urls)
        responses = await asyncio.gather(*pages)
    return responses


def find_urls_in_list(
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
        yield from find_urls_in_list(next_url, limit, acc + len(items))


def _parse_page(page_response: httpx.Response) -> str:
    page = page_response.text
    soup = BeautifulSoup(page, "html.parser")
    imdb_tag = soup.find("a", {"data-track-action": "IMDb"})
    if imdb_tag is None:
        raise MissingIMDbPage()
    assert isinstance(imdb_tag, Tag)
    imdb_url = imdb_tag.get("href")
    assert isinstance(imdb_url, str)
    tconst_match = re.match(imdb_pattern, imdb_url)
    assert tconst_match is not None
    tconst = tconst_match.group(1)
    return tconst


def download_urls(url_list: List[str]) -> List[str]:
    """
    Returns a list of tconsts.
    """
    result: List[str] = [''] * len(url_list)
    db = DBConnection()
    request_download = []
    request_index = []
    for i, page_url in enumerate(url_list):
        try:
            tconst = db.get_tconst(page_url)
            result[i] = tconst
        except KeyError:
            request_download.append(page_url)
            request_index.append(i)

    pages = asyncio.run(async_download_pages(request_download))
    for i, page in zip(request_index, pages):
        tconst = _parse_page(page)
        result[i] = tconst
        db.cache_url(url_list[i], tconst)
    return result


def download_list(list_url: str, limit: Optional[int] = None) -> Iterable[str]:
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
    page_urls = list(
        itertools.islice(find_urls_in_list(list_url, limit=numerical_limit), limit)
    )
    tconsts = download_urls(page_urls)
    return itertools.islice(tconsts, limit)
