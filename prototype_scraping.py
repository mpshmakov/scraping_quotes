import concurrent.futures
import threading
import uuid

import pandas as pd
from bs4 import Tag
from configuration import url
from database import Books, Session, TestTable, initDB, insertRow
from database.operations import check_tables_exist, initialize_schema
from sbooks import BeautifulSoup as bs
from sbooks import fetchPage, logger, requests
from sbooks.export_functions import exportToCsv, exportToJson
from sbooks.utils import clean_numeric
from sqlalchemy.exc import SQLAlchemyError
from tqdm import tqdm

# reminder:
# create 4 dataframes
# insert all tables into 1 json
# 4 csv files for each table

#*
# quote_page_worker:
#
# 1. get all quotes on page
#   1. add quote to quotes_list
#   2. if author is not in authors_list -> append author + about
#   3. if tag is not in tags_list -> append tag
#   4. add quote + tag to quotes_tags_link_list
# 
# *#

# questions for the meeting: there will be 4 csv files generated each time. is that fine?

# create a dict for all links of authors' abouts and parse them after quotes (should save time)

# after workers finish:
# 1. append quotes lists to each other
# 

def quote_page_worker(main_div: bs):
    div_quote_tags = main_div.find_all(class_="quote")
    id = str(uuid.uuid4()) # for debugging
    # uuid, quote, author
    quotes = []

    # list in list (for tags_quotes_link table)
    tags_relative_to_quotes = []

    # set which will be merged after all workers finish
    all_tags = set()

    # author : about link (to union all authors from workers afterwards (for authors table))
    authors = {}

    for div_quote_tag in div_quote_tags:
        

        author_span_tag = div_quote_tag.find_all("span")[1] # less robust approach but i think it should be faster
        author = author_span_tag.find(class_="author").get_text()
        author_about_link = author_span_tag.find("a")["href"].strip()
        print("author", author)
        print("about_link" , author_about_link)

        quote_uuid = str(uuid.uuid4()) 
        quote_text = div_quote_tag.find(class_="text").get_text().strip()
        quote = {quote_uuid: quote_uuid ,quote_text: quote_text, author: author}
        print("quote: ",id, quote)
        

        # an example of what i meant in whatsapp
        div_quote_tag = div_quote_tag.find_all()
        tags = div_quote_tag[5]["content"].split(",")
        print("tags",id, tags)
        print("\n\n")

        quotes.append(quote)
        authors[author] = author_about_link
        tags_relative_to_quotes.append(tags)
        for tag in tags:
            all_tags.add(tag)
    
    print("end")
    print("authors: ", authors)
    print("all_tags: ", all_tags)
    print("tags_relative_to_quotes: ", id, len(tags_relative_to_quotes))
    print("quotes: ",id, len(quotes))

    return {"authors": authors, "all_tags": all_tags, "tags_relative_to_quotes": tags_relative_to_quotes, "quotes": quotes}
        


response = fetchPage(url)
if response is None:
    raise Exception("Failed to fetch the Quotes page")

quote_page = bs(response.content, features="html.parser")
logger.info("Created the soup.")

quotes_pages = []
page_number = 1


while True:
    try:
        main_div = quote_page.find_all(class_="row")[1].find(class_="col-md-8")
        quotes_pages.append(main_div)
        next_page = main_div.find("nav").find("li", class_="next").find("a")["href"]

    except AttributeError:
        next_page = None

    print(next_page)
    if next_page != None:
        page_number += 1
        next_page_url = url + "page/" + str(page_number)
        # print("next page url: ",next_page_url)
        quote_page = bs(fetchPage(next_page_url).content, features="html.parser")
    else:
        break

print("len(quotes_pages)", len(quotes_pages))
    
with concurrent.futures.ThreadPoolExecutor() as executor:
    quotes_map = executor.map(quote_page_worker, quotes_pages)

#*
# 
# 
# 
# 
# 
# 
# *#

quotes = []
authors = {}
tags = set()

quote_tag_link = []

for result_dict in quotes_map:

    quotes_tmp = result_dict["quotes"]
    tags_tmp = result_dict["tags_relative_to_quotes"]

    for i in range(len(quotes_tmp)):
        for j in range(len(tags_tmp[i])):
            quote_tag_link.append([quotes_tmp[i]["quote_id"], tags_tmp[i][j]])
        
        quotes.append(quotes_tmp[i])

    tags.update(result_dict["all_tags"])
    authors.update(result_dict["authors"])

print("quotes", quotes)
print("authors: ", authors)
print("tags", tags)
print("quotes_tag_)link", quote_tag_link)

# quotes_df = pd.DataFrame(quotes)
# tags_arr = []
# for tag in tags:
#     tags_arr.append(tag)
# tags_df = pd.DataFrame(tags)