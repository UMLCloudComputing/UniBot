
# Python Packages
import fire
import json

# Local
from .api import API
from .course import Course
from .search import Search


# Formatter
def formatter(result):
    """Formats the python dictionary into pretty printed JSON. This is so the output when running as CLI
    is easier to read, but also when using the library as a module."""
    
    # If no result 
    if not result:
        return 'Formatter: No results found.'
    
    # If result is a dictionary, return pretty printed JSON
    if isinstance(result, dict):
        return json.dumps(result, indent=4)
    
    # Otherwise, return the result
    return result


# Create CLI

fire.Fire({
        'course': Course, 
        'search': Search, 
        'api': API
    }, 
    serialize=formatter,
)