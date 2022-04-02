import argparse
from functools import cache
import itertools
import math
import re
import sys
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

base_url = "https://letterboxd.com"
imdb_pattern = re.compile(r"http:\/\/www\.imdb\.com/title/(tt\d{7,8})/maindetails")

def _find_links_in_list(list_link, limit = float("inf"), acc = 0, pbar = None):
    """Finds all the links from a list"""
    if pbar is None:
        pbar = tqdm(total = math.ceil(limit / 72))

    response = requests.get(list_link)
    page = response.text
    soup = BeautifulSoup(page, "html.parser")
    table = soup.find("ul", class_="poster-list")
    items = table.find_all("li")
    movie_links = (f"{base_url}{li.div.get('data-film-slug')}" for li in items)
    yield from movie_links
    pbar.update(1)
    next_url_tag = soup.find("a", class_="next") 
    if next_url_tag and acc < limit:
        next_url = f"{base_url}{next_url_tag.get('href')}"
        yield from _find_links_in_list(next_url, limit, acc + len(items), pbar)
    else:
        pbar.close()


@cache
def _parse_link(movie_link):
    response = requests.get(movie_link)
    page = response.text
    soup = BeautifulSoup(page, "html.parser")
    imdb_tag = soup.find("a", {"data-track-action": "IMDb"})
    imdb_url = imdb_tag.get("href")
    imdb_id = re.match(imdb_pattern, imdb_url).group(1)
    return imdb_id


def download_list(list_link, limit=None):
    if limit is None:
        numerical_limit = float("inf")
    else:
        numerical_limit = limit

    movie_links = _find_links_in_list(list_link, limit=numerical_limit)
    imdb_ids = (_parse_link(movie) for movie in movie_links)
    return itertools.islice(imdb_ids, limit)

def parse_args(args):
    parser = argparse.ArgumentParser(description='Process letterbox link')
    parser.add_argument('url', metavar='url', type=str, help="The complete url to the letterboxd list")
    parser.add_argument('-limit', '-l', dest="limit", type=int, default=None)
    result = vars(parser.parse_args(args))
    if not result['url'].startswith('https://letterboxd.com/'):
        raise ValueError("Not a valid url.")
    return result


def main():
    args = parse_args(sys.argv[1:])
    print(list(download_list(args['url'], args['limit'])))

if __name__ == "__main__":
    main()