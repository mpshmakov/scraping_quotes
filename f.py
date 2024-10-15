from bs4 import BeautifulSoup as bs

from sbooks import fetchPage

about_page = bs(fetchPage("https://quotes.toscrape.com/author/J-K-Rowling/").content, features="html.parser")
about_text = about_page.find(class_="container").get_text()
print(about_text)