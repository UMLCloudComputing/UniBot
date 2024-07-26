from umlnow import course, Search, API
import re
import boto3
import os
import json

AWS_ID = os.getenv("AWS_ID")
AWS_KEY = os.getenv("AWS_KEY")
MAX_TOKEN = os.getenv("MAX_TOKEN", 256)

def invoke_llm(input):
    # Regex that filters out course IDs
    list = course_process(input)

    # Decide what user is asking about for courses
    outputText = LLMTitanLite(UMLNowAugment(input))

    print(outputText)

    match outputText:
        case "prerequisites":
            result = course_info("prereq", list[0])
            return result

        case "name": 
            result = course_info("name", list[0])
            return f"The name of {list[0]} is {result}"

        case _ if re.search(r"credits", outputText, re.IGNORECASE): 
            name = course_info("name", list[0])
            result = course_info("credits", list[0])
            return f"The course {name} is worth {result} credits"

def course_info(option, course_id):
    if option == "name":
        message_content = getCourse(course_id)
    elif option == "prereq":
        message_content = getPre(course_id)
    elif option == "credits":
        message_content = getCr(course_id)
    else:
        message_content = "Incorrect option"
    
    return message_content

def getCourse(courseID):
    return course.get_course_name(course.get_html_response(course.get_course_url(courseID)))

def getPre(courseID):
    return course.get_course_requirements_text(course.get_html_response(course.get_course_url(courseID)))

def getCr(courseID):
    dict = course.get_course_credits(course.get_html_response(course.get_course_url(courseID)))
    return f"Credits: {dict['min']}"

# Call The Titan Lite Model (No RAG Capabilities, only for decision making and scraping UML Now)
def LLMTitanLite(input):
    bedrock = boto3.client(
        service_name='bedrock-runtime', 
        region_name='us-east-1',
        aws_access_key_id=AWS_ID,
        aws_secret_access_key=AWS_KEY
        
    )

    modelId = 'amazon.titan-text-lite-v1'
    accept = 'application/json'
    contentType = 'application/json'
    body = json.dumps({
        "inputText": input,
        "textGenerationConfig":{
            "maxTokenCount": MAX_TOKEN,
            "stopSequences":[],
            "temperature":0,
            "topP":0.9
            }
    })

 
    response = bedrock.invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
    response_body = json.loads(response.get('body').read())
    return response_body.get('results')[0].get('outputText')

# Augmented Prompts
def UMLNowAugment(message):

    prompt_template3 = '''\n
    What is the user asking about for the course?? Choose from the following:
    prerequisites, name, credits.
    '''
    return message + prompt_template3

# Regex Matcher
def course_process(message):
    course_matches = []

    # Define the regex pattern for course identifiers
    course_pattern = r"(?i)([a-z]+)[ .]?(\d+)"

    # Search for matches in outputText and store them in the list
    matches = re.findall(course_pattern, message)
    for match in matches:
        # Format the match as 'PREFIX.NUMBER' and add to the list
        course_id = "{}.{}".format(match[0].upper(), match[1])
        course_matches.append(course_id)

    return course_matches