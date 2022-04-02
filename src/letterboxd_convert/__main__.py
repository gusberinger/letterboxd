from download import download_list
import argparse
import sys

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