"""
API
"""

# Python Packages
import requests
import datetime
import timeit


def get_term_code(year: int, season: str):
    """Returns the term code value from a year and season."""
    year_2015 = 25
    year_code = 0
    season_code = 0
    
    # Figure out year code
    year_code = year_2015 + abs(year - 2015)
    
    # Figure out season code
    if season.lower() == "fall": 
        season_code = 10
    if season.lower() == "winter": 
        season_code = 20
        year_code = year_code - 1
    if season.lower() == "spring": 
        season_code = 30
        year_code = year_code - 1
    if season.lower() == "summer": 
        season_code = 40
        year_code = year_code - 1
    
    return f"{year_code}{season_code}"

def get_term_name(term_code: str):
    """Returns the term name from a term code."""
    year = int(term_code[:2])
    season = int(term_code[2:])
    
    # Figure out year
    year = 2015 + abs(year - 25)
    
    # Figure out season
    if season == 10: 
        season = "Fall"
    if season == 20: 
        season = "Winter"
    if season == 30: 
        season = "Spring"
    if season == 40: 
        season = "Summer"
    
    return f"{season} {year}"

def get_all_semesters():
    """Returns a list of all current semester codes."""
    SEMESTER_CODES = []
    
    # Get current year
    current_year = datetime.datetime.now().year
    years = list(range(2015, current_year + 1))
    
    # For each year, get the semester codes
    for year in years:
        SEMESTER_CODES.append(get_term_code(year, "fall"))
        SEMESTER_CODES.append(get_term_code(year, "winter"))
        SEMESTER_CODES.append(get_term_code(year, "spring"))
        SEMESTER_CODES.append(get_term_code(year, "summer"))
        
    # Return semester codes
    return SEMESTER_CODES
    
# API
class API(object):
    """API Class.
    This object provides the CLI for the api command. This command is used to directly
    interface with the UML Now API and the UML Catalog API."""
    
    def __init__(self):
        """Initialize API Class"""
        pass
        
    def search(self, **params):
        """Search the UML Now API and return raw JSON."""
        # If no params:
        if not params:
            return "No params provided"
        
        # Base URL
        URL = "https://www.uml.edu/student-dashboard/api/ClassSchedule/RealTime/Search/?"
        
        # Create Request URL
        for key, value in params.items():
            URL += f"{key}={value}&"
                        
        # Request
        response = requests.get(URL).json()
        return response
    
    def search_history(self, course_number: str) -> dict:
        OUTPUT = {}
        prefix, number = course_number.split(".") 
        terms = get_all_semesters()
        total = 0
        start_time = timeit.default_timer()
        
        for term in terms:
            response = self.search(term=term, subjects=prefix, CatalogNumber=number)
            semester = response['data']['SearchFiltersUsed']['Term']['Description']
            total = total + response['data']['Count']
            
            # Disregard semesters with no results
            if response['data']['Classes']:
                OUTPUT[semester] = {}
                OUTPUT[semester]['Total'] = response['data']['Count']
                OUTPUT[semester]['Courses'] = []
                for course in response['data']['Classes']:
                    course_dict = {}
                    course_dict['Section'] = course['Section']
                    course_dict['Seats'] = course["Details"]['EnrollmentTotal']   
                    course_dict['Instructor'] = f"{course['Meetings'][0]['Instructors'][0]['Person']['FirstName']} {course['Meetings'][0]['Instructors'][0]['Person']['LastName']}"
                    
                    # for instructor in course['Meetings'][0]['Instructors']:
                    #     name = f"{instructor['Person']['FirstName']} {instructor['Person']['LastName']}"
                    #     course_dict['Instructors'].append(name)
                        
                    OUTPUT[semester]['Courses'].append(course_dict)
        
        OUTPUT['Time'] = timeit.default_timer() - start_time
        OUTPUT['Total'] = total
        return OUTPUT
    
    def catalog(self, **params):
        """Search the UML Course Catalog API and return raw JSON."""
        # Base URL
        URL = "https://www.uml.edu/catalog/advance-search.aspx?"
        
        # Create Request URL
        for key, value in params.items():
            URL += f"{key}={value}&"
            
        # Request
        response = requests.post(URL).json()
        return response    

