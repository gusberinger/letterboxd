import argparse
import re
from typing import Any, List, Dict

url_match = re.compile(r"(?:https?://)?(?:www\.)?(letterboxd\.com/.*)")


def parse_args(args: List[str]) -> Dict[str, Any]:
    parser = argparse.ArgumentParser(description='Process letterbox link')
    parser.add_argument('url', metavar='url', type=str,
                        help="The complete url to the letterboxd list")
    parser.add_argument('-limit', '-l', dest="limit", type=int, default=None)
    result = vars(parser.parse_args(args))
    url_body = re.match(url_match, result['url'])
    if url_body is None:
        raise ValueError("Not a valid letterboxd.com url")
    result['url'] = f"https://{url_body.group(1)}"
    return result
