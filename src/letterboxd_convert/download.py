import asyncio
import itertools
import logging
import re
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


def find_urls_in_single_list_page(soup: BeautifulSoup) -> Iterable[str]:
    """Finds all the urls from a single list page"""
    # soup = BeautifulSoup(page, "html.parser")
    poster_table = soup.find("ul", class_="poster-list")
    assert isinstance(poster_table, Tag)
    items = poster_table.find_all("li")
    movie_links = (f"{base_url}{li.div.get('data-film-slug')}" for li in items)
    yield from movie_links


def find_urls_in_list(list_url: str, limit: Optional[int]) -> Iterable[str]:
    first_page_response = httpx.get(list_url)
    first_page_soup = BeautifulSoup(first_page_response.text, "html.parser")
    yield from find_urls_in_single_list_page(first_page_soup)
    paginate_div = first_page_soup.find("div", class_="paginate-pages")

    # single-page list
    if paginate_div is None:
        return

    assert isinstance(paginate_div, Tag)
    last_page_li_tags = paginate_div.find_all("li")
    total_pages = int(list(last_page_li_tags)[-1].text)

    page_urls = [f"{list_url}page/{i}/" for i in range(2, total_pages + 1)]
    page_respones = asyncio.run(async_download_pages(page_urls))
    page_soups = (
        BeautifulSoup(response.text, "html.parser") for response in page_respones
    )
    found_urls = itertools.chain(
        *(find_urls_in_single_list_page(soup) for soup in page_soups)
    )
    yield from itertools.islice(found_urls, limit)


def _parse_page(page_response: httpx.Response) -> str:
    page = page_response.text
    tconst_match = re.search(imdb_pattern, page)
    if tconst_match is None:
        raise MissingIMDbPage()
    tconst = tconst_match.group(1)
    return tconst


def download_urls(url_list: List[str]) -> Iterable[str]:
    """
    Returns a list of tconsts.
    """
    result: List[str] = [""] * len(url_list)
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
        try:
            tconst = _parse_page(page)
            result[i] = tconst
            db.cache_url(url_list[i], tconst)
        except MissingIMDbPage:
            result[i] = ""
            logging.warn(
                f"Skipping movie at url {url_list[i]}. "
                "No corresponding IMDb page listed."
            )
    return filter(bool, result)


def download_list(list_url: str, limit: Optional[int] = None) -> Iterable[str]:
    """
    Parameters
    ___
    list_url:
        The url to the letterboxd.com list.
    limit:
        The maximum number of movies to fetch from the list.
    """
    page_urls = list(find_urls_in_list(list_url, limit))
    tconsts = download_urls(page_urls)
    return itertools.islice(tconsts, limit)
