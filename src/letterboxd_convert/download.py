import logging
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
    imdb_id_match = re.match(imdb_pattern, imdb_url)
    assert imdb_id_match is not None
    imdb_id = imdb_id_match.group(1)
    return imdb_id


def download_urls(url_list: Iterable[str]) -> Iterable[str]:
    """
    Returns a list of tconsts.
    """
    db = DBConnection()
    for page_url in url_list:
        try:
            tconst = db.get_tconst(page_url)
            yield tconst
        except KeyError:
            page = httpx.get(page_url)
            tconst = _parse_page(page)
            db.cache_url(page_url, tconst)
            yield tconst
        except MissingIMDbPage as e:
            logging.warn(f"Movie at url:{page_url} has no IMDb page.")


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
    page_urls = find_urls_in_list(list_url, limit=numerical_limit)
    tconsts = download_urls(page_urls)
    return itertools.islice(tconsts, limit)
