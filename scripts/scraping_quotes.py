import concurrent.futures
import threading
import uuid

import pandas as pd
from bs4 import Tag
from configuration import get_configuration
from database import initDB, insertRow, Authors, Tags, Quotes, QuotesTagsLink, TestTable
from database.operations import check_tables_exist, initialize_schema, updateAuthorRowAboutValue
from squotes import BeautifulSoup as bs
from squotes import fetchPage, logger, requests
from squotes.export_functions import exportMultipleDfsToOneJson, exportToCsv
from squotes.utils import clean_numeric
from sqlalchemy.exc import SQLAlchemyError
from tqdm import tqdm
import json


# reminder:
# create 4 dataframes
# insert all tables into 1 json
# 4 csv files for each table
# insert data into db while parsing it

# can't seem to handle sqlalchemy.exc.IntegrityError exceptions so i insert authors and tags outside of quotes_worker

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

pbar_quotes = tqdm(total=100, desc="quotes")
pbar_tags = tqdm(total=138, desc="tags")
pbar_authors = tqdm(total=50, desc="authors")
pbar_quote_tag_link = tqdm(total=235, desc="quotes_tags_links")

configuration = get_configuration()
#print(type(configuration))
# print((json.dumps(configuration)))
logger.info("configuration extracted: " + str(configuration)) # this line doesn't work


def update_pagesnum():    
    url = configuration["url"]
    pagesnum = configuration["pagesnum"]

    addendant = 2
    next_page_url = url + "page/" + str(pagesnum + 1)
    quote_page = bs(fetchPage(next_page_url).content, features="html.parser")

    while True:
        try:
            main_div = quote_page.find_all(class_="row")[1].find(class_="col-md-8")
            next_page = main_div.find("nav").find("li", class_="next").find("a")["href"]

        except AttributeError:
            next_page = None

        if next_page != None:
            next_page_url = url + "page/" + str(pagesnum + addendant)
            quote_page = bs(fetchPage(next_page_url).content, features="html.parser")
            addendant = addendant + 1
        else:
            #update configuration.json pagesnum value
            with open("configuration.json", "r") as jsonFile:
                data = json.load(jsonFile)
                data["pagesnum"] = pagesnum + (addendant-1)
                jsonFile.close()

            with open("configuration.json", "w") as jsonFile:
                json.dump(data, jsonFile)
                jsonFile.close()
            break


def check_for_new_pages_and_update_pagesnum():
    """
    Checks if pagesnum + 1 from configuration.json exists. If they do, updates pagesnum in configuration.json

    Returns:
        True or False. True if new pages exist, False if they don't. 
    """
    url = configuration["url"]
    pagesnum = configuration["pagesnum"]

    next_page_url = url + "page/" + str(pagesnum)
    quote_page = bs(fetchPage(next_page_url).content, features="html.parser")
    try:
        main_div = quote_page.find_all(class_="row")[1].find(class_="col-md-8")
        next_page = main_div.find("nav").find("li", class_="next").find("a")["href"]

    except AttributeError:
        return False
    
    logger.info("more pages of quotes detected.")
    update_pagesnum()
    logger.info("updated pagesnum in configuration.")
    return True


def quote_page_worker(page_url: str):
    quote_page = bs(fetchPage(page_url).content, features="html.parser")
    main_div = quote_page.find_all(class_="row")[1].find(class_="col-md-8")

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
        ##print("author", author)
        ##print("about_link" , author_about_link)

        quote_uuid = str(uuid.uuid4()) 
        quote_text = div_quote_tag.find(class_="text").get_text().strip()
        quote = {"quote_uuid": quote_uuid ,"quote_text": quote_text, "author": author}
        ##print("quote: ",id, quote)
        

        # an example of what i meant in whatsapp
        div_quote_tag = div_quote_tag.find_all()
        tags = div_quote_tag[5]["content"].split(",")
        ##print("tags",id, tags)
        ##print("\n\n")

        quotes.append(quote)
        authors[author] = author_about_link
        tags_relative_to_quotes.append(tags)
        for tag in tags:
            all_tags.add(tag)
            tag_row = Tags(tag=tag)
            insertRow(tag_row)
        
        author_row = Authors(author, author_about_link) #need to insert data into authors table before quotes because of FK. update about info later
        insertRow(author_row)

        quote_row = Quotes(quote_uuid, quote_text, author)
        insertRow(quote_row)
        pbar_quotes.update(1)

        logger.info("scraped: quote: " + str(quote) + "; author: "+ author + "; tags: "+ str(tags))


    ##print("end")
    ##print("authors: ", authors)
    ##print("all_tags: ", all_tags)
    ##print("tags_relative_to_quotes: ", id, len(tags_relative_to_quotes))
    ##print("quotes: ",id, len(quotes))

    


    #print("inserted for page ", page_url)

    return {"authors": authors, "all_tags": all_tags, "tags_relative_to_quotes": tags_relative_to_quotes, "quotes": quotes}

# basically changes about from url to the description text of the author (done separately from quote worker to potentially save execution time)
def authors_worker(author):
    about_url = configuration["url"] + author["about"].split("/", 1)[1]
    ##print("about_url", about_url)
    about_page = bs(fetchPage(about_url).content, features="html.parser")
    about_text = about_page.find(class_="author-details").get_text()
    updateAuthorRowAboutValue(author["author"], about_text)

    logger.info(f"parsed {author["author"]}'s about page")
    return {"author": author["author"], "about": about_text}


def check_structure_changes(response):
    response_soup = bs(response.content, features="html.parser")
    structure_check = response_soup.find_all(class_="col-md-8")[1].find(class_="quote")
    # #print(structure_check)
    if structure_check is None:
        raise Exception("Page structure has changed.")
    logger.info("page structure hasn't changed.")


def main():
    global configuration

    response = fetchPage(configuration["url"])
    if response is None:
        raise Exception("Failed to fetch the Quotes page")

    check_structure_changes(response)
    
    quotes_pages_urls = []

    # 10 pages exist for sure.
    # create a function which checks if 11th page exists. if true, iterate and change pages number in configuration.json

    check_for_new_pages_and_update_pagesnum()
    configuration = get_configuration()

    url = configuration["url"]
    pagesnum = configuration["pagesnum"]

    for i in range(pagesnum):
        next_page_url = url + "page/" + str(i+1)
        quotes_pages_urls.append(next_page_url)

    ##print("len(quotes_pages)", len(quotes_pages_urls))
    
    initDB()
        
    with concurrent.futures.ThreadPoolExecutor() as executor:
        quotes_map = executor.map(quote_page_worker, quotes_pages_urls)


    quotes = []
    authors = {}
    tags = set()

    quote_tag_link = []

    #quotes and tags_quote_link
    for result_dict in quotes_map:

        quotes_tmp = result_dict["quotes"]
        tags_tmp = result_dict["tags_relative_to_quotes"]

        for i in range(len(quotes_tmp)):
            for j in range(len(tags_tmp[i])):
                quote_tag_link.append({"quote_uuid": quotes_tmp[i]["quote_uuid"], "tag": tags_tmp[i][j]})
                quote_tag_link_row = QuotesTagsLink(quotes_tmp[i]["quote_uuid"], tags_tmp[i][j])
                pbar_quote_tag_link.update(1)
                insertRow(quote_tag_link_row)

            quotes.append(quotes_tmp[i])

        tags.update(result_dict["all_tags"])
        pbar_tags.reset()
        pbar_tags.update(len(tags))
        pbar_tags.refresh()
        authors.update(result_dict["authors"])
        pbar_authors.reset()
        pbar_authors.update(len(authors))
        pbar_authors.refresh()

    tags = list(tags)

    authors_list = []
    for author in authors:
        authors_list.append({"author":author, "about":authors[author]})

    # authors
    with concurrent.futures.ThreadPoolExecutor() as executor:
        authors_map = executor.map(authors_worker, authors_list)

    authors = []
    for author in authors_map:
        authors.append(author)


    #print("quotes", len(quotes))
    #print("authors: ", len(authors))
    #print("tags", len(tags))
    #print("quotes_tag_)link", len(quote_tag_link))

    quotes_df = pd.DataFrame(quotes)
    quote_tag_df = pd.DataFrame(quote_tag_link)
    tags_df = pd.DataFrame(tags)
    authors_df = pd.DataFrame(authors)

    exportToCsv(quotes_df, "quotes.csv")
    exportToCsv(quote_tag_df, "quote_tag_link")
    exportToCsv(tags_df, "tags")
    exportToCsv(authors_df, "authors")

    df_arr = [quotes_df, quote_tag_df, tags_df, authors_df]
    df_names_arr = ["quotes", "quotes_tags_link", "tags", "authors"]

    exportMultipleDfsToOneJson(df_arr=df_arr, df_names_arr=df_names_arr)

    # exportToJson(quotes_df, "quotes")
    # exportToJson(quote_tag_df, "quote_tag_link")
    # exportToJson(tags_df, "tags")
    # exportToJson(authors_df, "authors")

    #create pk tables first, fk second

    ##print(quotes_df.head())
    ##print(quote_tag_df.head())
    ##print(tags_df.head())
    ##print(authors_df.head())

if __name__ == "__main__":
    main()