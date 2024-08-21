# An Extraction Library for UMass Lowell Website

import json
import requests
import re
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

INDEX_NAME = os.getenv("INDEX_NAME")

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

def insert_chunk(chunk, chunk_number, prefix):
    markdown_output = ""
    for course in chunk:
        # Json to markdown
        markdown_output += json_to_markdown(course)
        markdown_output += "\n\n"

    # Write to file
    url = f"https://www.uml.edu/Catalog/Advanced-Search.aspx?prefix={prefix}&type=prefix#{chunk_number}"
    pc.insert_document(INDEX_NAME, [markdown_output], [url])

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


def extract_courses():
    vector = pc.get_vector_index(INDEX_NAME)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for prefix in DEPARTMENT_PREFIXES:
            result = requests.get(f"https://www.uml.edu/api/registrar/course_catalog/v1.0/courses?field=subject&query={prefix}")
            courses = result.json()

            for i in range(0, len(courses), CHUNK_SIZE):
                chunk = courses[i:i + CHUNK_SIZE]
                chunk_number = i // CHUNK_SIZE + 1
                futures.append(executor.submit(insert_chunk, chunk, chunk_number, prefix))

        # Wait for all futures to complete
        concurrent.futures.wait(futures)

if __name__ == "__main__":
    extract_courses()