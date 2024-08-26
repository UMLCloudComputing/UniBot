# An Extraction Library for UMass Lowell Website

import json
import requests
import re
import difflib
import os
import vector as pc
import concurrent.futures
from dotenv import load_dotenv
load_dotenv()

CHUNK_SIZE = 10

DEPARTMENT_PREFIXES = [
    "ACCT",
    "AERO",
    "AEST",
    "AMHE",
    "AMST",
    "ARCH",
    "ARHI",
    "ARTS",
    "ASAM",
    "ATMO",
    "BIOL",
    "BMBT",
    "BMEN",
    "BMSC",
    "BOST",
    "BUSI",
    "CHEM",
    "CHEN",
    "CIVE",
    "COMP",
    "CONT",
    "CORE",
    "CRIM",
    "DART",
    "DGMD",
    "DPTH",
    "ECON",
    "EDUC",
    "EECE",
    "ENGL",
    "ENGN",
    "ENGY",
    "ENTR",
    "ENVE",
    "ENVI",
    "ENVS",
    "ETEC",
    "EXER",
    "FAHS",
    "FINA",
    "GEOL",
    "GLST",
    "GNDR",
    "GRFX",
    "HIST",
    "HONR",
    "HSCI",
    "IENG",
    "IM",
    "INFO",
    "LABR",
    "LGST",
    "LIFE",
    "LMUCM",
    "MARI",
    "MATH",
    "MECH",
    "MGMT",
    "MIST",
    "MKTG",
    "MLSC",
    "MPAD",
    "MSIT",
    "MTEC",
    "MUAP",
    "MUBU",
    "MUCM",
    "MUED",
    "MUEN",
    "MUHI",
    "MUPF",
    "MUSR",
    "MUTH",
    "NONC",
    "NURS",
    "NUTR",
    "PCST",
    "PHIL",
    "PHRM",
    "PHYS",
    "PLAS",
    "POLI",
    "POLY",
    "POMS",
    "PSMA",
    "PSYC",
    "PTEC",
    "PUBH",
    "RADI",
    "ROTC",
    "SCIE",
    "SOCI",
    "THEA",
    "UGTC",
    "UMLO",
    "UNCR",
    "UTCH",
    "WLAN",
    "WLAR",
    "WLCH",
    "WLFR",
    "WLGE",
    "WLIT",
    "WLKH",
    "WLLA",
    "WLPO",
    "WLSP",
    "WORC",
]

INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

# Function to convert JSON to Markdown
def json_to_markdown(course):
    title = course["Title"]
    title = re.sub(r'\s*\(Formerly.*?\)', '', title)
    course_id = course["Department"] + "." + course["CatalogNumber"]
    description = course["Description"]
    credits = course["UnitsMinimum"]
    career = course["AcademicCareer"]["Description"]
    requirements = course["EnrollmentRequirements"]

    markdown = f"# {title} (course ID: {course_id}) ({career} course)\n\n"
    markdown += f"## Description:\n{description}\n\n"
    markdown += f"## Credits: {credits}\n\n"
    markdown += f"## Prerequisites:\n{requirements}\n\n"

    return markdown

def extract(soup):
    # Remove Headers, Footers, and Sidebars
    # List of selectors to find and decompose
    selectors = [
        ("footer", "layout-footer"),
        ("div", "layout-header__inside"),
        ("div", "layout-header__nav"),
        ("div", "layout-header__quick-links"),
        ("div", "l-supplemental-content"),
        ("div", "l-page__nav"),
        ("div", "c-browser-support-message")
    ]

    # Decompose elements based on selectors
    for tag, class_name in selectors:
        elements = soup.find_all(tag, class_=class_name)
        for element in elements:
            element.decompose()


    parsed_text = ""

    title_tag = soup.find('title')
    if title_tag:
        parsed_text += f"# {title_tag.get_text(strip=True)}\n\n"

    for element in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'table']):
        tag_name = element.name
        text_content = element.get_text(strip=True)

        if tag_name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            parsed_text += f"## {text_content}\n\n"
        elif tag_name == 'ul':
            markdown_list = [f"- {li.text.strip()}" for li in element.find_all('li')]
            markdown_output = "\n".join(markdown_list)
            parsed_text += f"{markdown_output}\n\n"
        elif tag_name == 'table':
            parsed_text += str(element) + "\n\n"
        else:
            parsed_text += f"{text_content}\n\n"

    return parsed_text

def extract_course_helper(prefix):
    print(f"Inserting courses {prefix} into dictionary")
    result = requests.get(f"https://www.uml.edu/api/registrar/course_catalog/v1.0/courses?field=subject&query={prefix}")
    courses = result.json()
    return courses
    # with concurrent.futures.ThreadPoolExecutor() as executor:
    #     futures = []
    #     for i in range(0, len(courses), batch_size):
    #         batch = courses[i:i + batch_size]
    #         documents = [json_to_markdown(course) for course in batch]
    #         urls = [f"https://www.uml.edu/Catalog/Courses/{course['Department']}/{course['CatalogNumber']}" for course in batch]
    #         # print(f"Inserting {len(batch)} courses")
    #         futures.append(executor.submit(pc.insert_document, INDEX_NAME, documents, urls))

    #     # Check for exceptions
    #     for future in concurrent.futures.as_completed(futures):
    #         try:
    #             future.result()
    #         except Exception as e:
    #             print(f"Error processing batch: {e}")


def extract_courses():
    course_dict = {}

    with concurrent.futures.ThreadPoolExecutor() as outer_executor:
        for prefix in DEPARTMENT_PREFIXES:
            course_dict[prefix] = outer_executor.submit(extract_course_helper, prefix).result()
    
    return course_dict

def insert_courses(index_name):
    course_dict = extract_courses()
    futures = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for key in course_dict:
            course_list = course_dict[key]
            for course in course_list: 
                document = json_to_markdown(course)
                url = f"https://www.uml.edu/Catalog/Courses/{course['Department']}/{course['CatalogNumber']}"
                file_name = f"data/dataset/{url.replace('/', '_')}.json"
                if os.path.exists(file_name):
                    with open(file_name, "r") as file:
                        content = json.load(file)
                        if (content["text"] != document):
                            print(f"Updated Course {url}")
                            futures.append(executor.submit(pc.insert_document, index_name, [document], [url]))
                        else:
                            print(f"Course {url} already exists")
                else:
                    print(f"New Course {url}")
                    executor.submit(pc.insert_document, index_name, [document], [url])

if __name__ == "__main__":
    extract_courses()