## Scraping Quotes

Quotes to Scrape is a mock online bookstore designed for web scraping activities. It offers a diverse catalog of books across various genres, complete with pricing, availability, and star ratings, making it an excellent resource for engineers to sharpen their data extraction skills.

### Install Dependencies

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install following

```python
## Prerequisites
python3 -m venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt
python3 -m pip install --upgrade pip
deactivate
```

### Usage

```python
## Actual Application
python3 -m scripts.scraping_quotes

## Unit Test with Coverage
coverage run -m pytest

## Generate Coverage Report
coverage report -m

## Pytest
pytest
```

> You can keep the `data` directory. It's a small project, so you are not storing large files in the repository.

### Current Code Coverage

### Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/moatsystems/imdb_scrapy/tags).

### License

This project is licensed under the [BSD 3-Clause License](LICENSE) - see the file for details.

### Copyright

(c) 2024 [Maksim Shmakov](https://coming.com).
