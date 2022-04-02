from .download import download_list
from .parse import parse_args
import sys


def main():
    args = parse_args(sys.argv[1:])
    print(list(download_list(args['url'], args['limit'])))


if __name__ == "__main__":
    main()
