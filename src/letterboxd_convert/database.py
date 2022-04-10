import sqlite3
from pathlib import Path


class ConfigFolderTakenException(Exception):
    """Cannot create the $HOME/.letterboxd/ directory. File already exists."""


CONFIG_PATH = Path.home().joinpath(".letterboxd/")
if not CONFIG_PATH.exists():
    CONFIG_PATH.mkdir()
elif CONFIG_PATH.is_file():
    raise ConfigFolderTakenException()

DB_PATH = CONFIG_PATH.joinpath("cache.db")


create_table_query = """
CREATE TABLE IF NOT EXISTS cache (
    url varchar(255),
    tconst varchar(255)
)
"""


class DBConnection:
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(DBConnection)
            return cls.instance
        return cls.instance

    def __init__(self) -> None:
        self.con = sqlite3.connect(DB_PATH)
        self.cursor = self.con.cursor()
        self.cursor.execute(create_table_query)
        movies_req = self.cursor.execute("SELECT url, tconst FROM cache")
        self.movies = dict(movies_req.fetchall())

    def __del__(self) -> None:
        self.cursor.close()
        self.con.close()

    def get_tconst(self, url: str) -> str:
        return self.movies[url]

    def cache_url(self, url: str, tconst: str) -> None:
        self.cursor.execute("INSERT INTO cache values (?, ?)", (url, tconst))
        self.movies[url] = tconst
        self.con.commit()

    def clear_cache(self) -> None:
        self.cursor.execute("DROP TABLE cache")
        self.cursor.execute(create_table_query)
        self.movies = {}
