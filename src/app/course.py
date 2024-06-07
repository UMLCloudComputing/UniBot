"""
Courses
"""

# Python Packages
from bs4 import BeautifulSoup
import requests
import json
import functools

# Local
from data import DEPARTMENT_PREFIXES
from api import API


# Intialize API
API = API()


def get_course_url(course: str):
    """Get the url for a course."""
    prefix, number = course.split(".")
    return f"https://www.uml.edu/catalog/courses/{prefix}/{number}/"

def get_html_response(url: str):
    """Get the html response from a url."""
    
    # Get the response
    response = requests.get(url)
    
    # Check if course page exists
    soup = BeautifulSoup(response.content, "html.parser")
    if soup.select("#PrimaryContentPlaceHolder_searchControl_lblNoResult"):
        if soup.select("#PrimaryContentPlaceHolder_searchControl_lblNoResult")[0].text == "No results found.":
            return None
    
    # Otherwise, return the response
    return response

def get_course_name(response: requests.models.Response):
    """Returns the course name as a string from a html response."""
    try:
        soup = BeautifulSoup(response.content, "html.parser")
        html = soup.select("h1")[0]
        return html.text
    except:
        return ""

def get_course_description(response: requests.models.Response):
    """Returns the course description as a string from a html response."""
    try:
        soup = BeautifulSoup(response.content, "html.parser")
        html = soup.select("p:nth-child(5)")[0]
        return html.text
    except:
        return ""

def get_course_id(response: requests.models.Response):
    """Returns the course id as a string from a html response."""
    try: 
        soup = BeautifulSoup(response.content, "html.parser")
        course_id = soup.select(".outline:nth-child(1)")[0].text
        
        # Sanitize
        if "id:" in course_id.lower(): course_id = course_id.split("Id: ")[1]
        
        # return 
        return course_id
    
    except:
        return ""

def get_course_credits(response: requests.models.Response):
    """Returns the course credits as a dict from a html response."""
    try: 
        soup = BeautifulSoup(response.content, "html.parser")
        min_credits = soup.select(".outline:nth-child(2)")[0].text
        max_credits = soup.select(".outline:nth-child(3)")[0].text
        
        # Sanitize
        if 'credits' in min_credits.lower(): min_credits = min_credits.split("Credits Min: ")[1]
        if 'credits' in max_credits.lower(): max_credits = max_credits.split("Credits Max: ")[1]
        
        # Return
        return {
            'min': min_credits,
            'max': max_credits,
        }
    
    except:
        return {
            'min': '',
            'max': '',
        }

def get_course_requirements_text(response: requests.models.Response):
    """Returns the course requirements as a string from a html response."""
    try:
        soup = BeautifulSoup(response.content, "html.parser")
        html = soup.select("p:nth-child(7)")[0]
        return html.text
    except:
        return ""
    
def extract_courses_from_str(text: str):
    """Returns a list of courses from a string."""
    output = []
    
    # Replacement rules to make parsing accurate
    text = text.replace(", or", "or")
    text = text.replace("and", ",")
    
    # Break string by "," into list and iterate to get requirements
    for requirement in text.split(","):
        requirement_output = []
        
        # Break requirement string into list. This should put the course prefix right before the course number in the list.
        requirement_list = requirement.replace('.', ' ').split(" ")

        # Iterate through list and find course prefixes
        for index, item in enumerate(requirement_list):
            
            # If item is a course prefix, append to output
            if item.lower() in [prefix.lower() for prefix in DEPARTMENT_PREFIXES]:
                
                # Make sure the next element in list exists, otherwise this is is not a valid course prefix
                if index + 1 < len(requirement_list):
                    
                    # Make sure next element in list is a 4 or 5 letter number (like COMP.1010 or COMP.1030L)
                    if len(requirement_list[index + 1]) == 4 or len(requirement_list[index + 1]) == 5:
                        requirement_output.append(f"{item}.{requirement_list[index + 1]}".upper())
                
        # Append to output, if not empty
        if requirement_output: output.append(requirement_output)

    return output
    
def get_course_requirements_dict(text: str) -> dict:
    """Returns a parsed dictionary from the course requirements string."""
    
    # Output    
    output = {
        "prerequisites": [],
        "corequisites": [],
    }
    
    # Need to split the text into two parts, one for prereqs and one for coreqs.
    prereqs = ""
    coreqs = ""
    antireqs = ""
    
    # If "Anti-req" in text, we have problems. Split the string into antireqs and discard the rest.
    if "anti-req" in text.lower():
        text = text.lower().split("anti-req", maxsplit=1)[0]
    
    # If "Co-req" in text, split into prereqs and coreqs. We are assuming this gives a list with two strings.
    if "co-req" in text.lower():
        prereqs, coreqs = text.lower().split("co-req", maxsplit=1)
        
    # Otherwise assume prereqs are all text
    else:
        prereqs = text.lower()
    
    output['prerequisites'] = extract_courses_from_str(prereqs)
    output['corequisites'] = extract_courses_from_str(coreqs)
    
    # Return output
    return output

def filter_by_instructor(data, instructor):
    """Filter an API data response by instructor."""
    filtered_data = {}
    for term, term_data in data.items():
        if term == "Time" or term == "Total":
            continue
        filtered_courses = [course for course in term_data["Courses"] if course['Instructor'].lower().split(" ") == instructor]
        if filtered_courses:
            filtered_data[term] = {"Total": len(filtered_courses), "Courses": filtered_courses}
    return filtered_data

def filter_by_semester(data, semester):
    filtered_data = {}
    for term, term_data in data.items():
        if term == "Time" or term == "Total":
            continue
        if semester.lower() in term.lower():
            filtered_data[term] = term_data
    return filtered_data

# Course Command
def Course(course, **kwargs):
    """ """
    
    # If debug, print starting message
    if kwargs.get("debug"):
        print("    - Starting: " + course)
        
    # History
    if kwargs.get("history"):
        history = API.search_history(course)
        
        # If both professor and semester flags passed, filter history for professor and semester
        if kwargs.get("prof") and kwargs.get("semester"):
            professor = list(kwargs.get("prof"))
            semester = kwargs.get("semester")
            return filter_by_semester(filter_by_instructor(history, professor), semester)

        # If professor flag passed, filter history for professor
        if kwargs.get("prof"):
            professor = list(kwargs.get("prof"))
            return filter_by_instructor(history, professor)
        
        # If semester flag passed, filter history for semester
        if kwargs.get("semester"):
            semester = kwargs.get("semester")
            print(semester)
            return filter_by_semester(history, semester)
        
        # Otherwise, return history unfiltered
        return history
    
    # Create course url lookup from "course"
    course_url = get_course_url(course)
    
    # Get html response
    response = get_html_response(course_url)
    if not response: return {'error': "Course does not exist."}

    requirements_text = get_course_requirements_text(response)
    parsed_requirements = get_course_requirements_dict(requirements_text)
    course_name = get_course_name(response)
    course_description = get_course_description(response)
    course_id = get_course_id(response)
    course_credits = get_course_credits(response)
    
    # Filter results based on kwargs
    if kwargs.get('name'): return {'name': course_name,}
    if kwargs.get('url'): return {'url': course_url,}
    if kwargs.get('id'): return {'id': course_id,}
    if kwargs.get('description'): return {'description': course_description,}
    if kwargs.get('credits'): return {'credits': course_credits,}
    if kwargs.get('requirements_text'): return {'requirements-text': requirements_text,}
    if kwargs.get('requirements'): return {'requirements': parsed_requirements,}
    
    # Otherwise, return all results
    return {
        'name': course_name,
        'url': course_url,
        'id': course_id,
        'description': course_description,
        'credits': course_credits,
        'requirements-text': requirements_text,
        'requirements': parsed_requirements,
    }