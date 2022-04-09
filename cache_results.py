from dataclasses import dataclass
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
        movies_req = self.cursor.executemany("SELECT url, tconst FROM cache")
        movies = dict(movies_req.fetchall())

    def __del__(self) -> None:
        self.cursor.close()
        self.con.close()

    # def fetch_movies(self, url_list: List[str]):
