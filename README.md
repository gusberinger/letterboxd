# letterboxd-convert
![Tests](https://github.com/gusberinger/letterboxd-convert/actions/workflows/tests.yml/badge.svg)

Convert letterboxd.com lists to a list of imdb ids.

## Usage

CLI usage
```
letterboxd-convert "https://letterboxd.com/crew/list/the-2010s-top-250-narrative-features/" -limit 20
```


Python package

```
from letterboxd_convert import download_list
url = "https://letterboxd.com/crew/list/the-2010s-top-250-narrative-features/"
print(download_list(url, limit=20))
```
