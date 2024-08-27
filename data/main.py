from urllib.parse import urlparse
import json
import os
import requests
from bs4 import BeautifulSoup
import lxml
import argparse
import uml
import re
import vector as pc
import concurrent.futures
from dotenv import load_dotenv
load_dotenv()

def extract_tags(soup, pattern):
    print("Extracting tags")
    tags_dict = {}
    loc_text = None

    for element in soup.find_all(['loc', 'lastmod']):
        if element.name == 'loc' and pattern.search(element.get_text()):
            loc_text = element.get_text()
            tags_dict[loc_text] = None
        elif element.name == 'lastmod' and loc_text:
            tags_dict[loc_text] = element.get_text()
            loc_text = None

    print("Tags extracted and dictionary created")
    print(f"Number of items in dictionary: {len(tags_dict)}")
    return tags_dict

def get_dict(substrings: list, sitemap_url: str):
    response = requests.get(sitemap_url)
    soup = BeautifulSoup(response.content, 'lxml')
    return extract_tags(soup, re.compile('|'.join(substrings)))

def upsert(url):
    # print(f"Processing URL {url}")
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    parsed_text = uml.extract(soup)

    file_name = f"data/dataset/{url.replace('/', '_')}.json"
    if os.path.exists(file_name):
        with open(f"data/dataset/{url.replace('/', '_')}.json", "r") as file:
            content = json.load(file)
            if (content["text"] != parsed_text):
                print(f"Changes detected in {url}")
                pc.insert_document(os.getenv("PINECONE_INDEX_NAME"), [parsed_text], [url])    
    else:
        print(f"New URL {url}")
        pc.insert_document(os.getenv("PINECONE_INDEX_NAME"), [parsed_text], [url])

def main():
    # Open urls.json file
    with open('urls.json') as f:
        urls = json.load(f)

    substrings  = urls['urls']
    tags_dict = get_dict(substrings, urls["sitemap"])
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for url in tags_dict:
            executor.submit(upsert, url)
            

if __name__ == "__main__":
    # If argument "import" is set, import the documents using argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--importdata", action="store_true")
    parser.add_argument("--courses", action="store_true")
    args = parser.parse_args()
    if args.importdata:
        print("Importing data")
        pc.get_vector_index(os.getenv("PINECONE_INDEX_NAME"))
        pc.import_documents(os.getenv("PINECONE_INDEX_NAME"), 10)
    elif args.courses:
        print("Extracting courses")
        result = uml.insert_courses(os.getenv("PINECONE_INDEX_NAME"))
        print(result)
    else:
        print("Running main")
        pc.get_vector_index(os.getenv("PINECONE_INDEX_NAME"))
        main()