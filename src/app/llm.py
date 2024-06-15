from umlnow import course, Search, API
import re
import course
import boto3
import json
import os

BEDROCK_ID = os.getenv("BEDROCK_ID")
BEDROCK_KEY = os.getenv("BEDROCK_KEY")
KNOWLEDGE = os.getenv("KNOWLEDGE_BASE_ID")

def invoke_llm(input):
    isCourse = LLMTitanLite(input + isCourseAugment(input))

    if isCourse == "yes":
        # Regex that filters out course IDs
        list = course_process(input)

        # Decide what user is asking about for courses
        outputText = LLMTitanLite(UMLNowAugment(input))

        match outputText:
            case "prerequisites": return course.course_info("prereq", list[0])
            case "name": return course.course_info("name", list[0])
            case "credits": return course.course_info("credits", list[0])

    else:
        return LLMTitanPremier(RAGTemplate(input))

# Call The Titan Lite Model (No RAG Capabilities, only for decision making and scraping UML Now)
def LLMTitanLite(input):
    bedrock = boto3.client(
        service_name='bedrock-runtime', 
        region_name='us-east-1',
        aws_access_key_id=os.getenv("BEDROCK_ID"),
        aws_secret_access_key=os.getenv("BEDROCK_KEY")
        
    )

    modelId = 'amazon.titan-text-lite-v1'
    accept = 'application/json'
    contentType = 'application/json'
    body = json.dumps({
        "inputText": input,
        "textGenerationConfig":{
            "maxTokenCount":256,
            "stopSequences":[],
            "temperature":0,
            "topP":0.9
            }
    })

 
    response = bedrock.invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
    response_body = json.loads(response.get('body').read())
    return response_body.get('results')[0].get('outputText')

# Call the Titan Premier Model (RAG Capabilities)
def LLMTitanPremier(input):
    bedrock = boto3.client(
        service_name='bedrock-agent-runtime', 
        region_name='us-east-1',
        aws_access_key_id=BEDROCK_ID,
        aws_secret_access_key=BEDROCK_KEY
            
    )   
    return bedrock.retrieve_and_generate(
        input={
            'text': input
        },
        retrieveAndGenerateConfiguration={
            'type': 'KNOWLEDGE_BASE',
            'knowledgeBaseConfiguration': {
                'knowledgeBaseId': KNOWLEDGE,
                'modelArn': 'arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-text-premier-v1:0'
                }
            }
        )["output"]["text"]

# Augmented Prompts
def UMLNowAugment(message):

    prompt_template3 = '''\n
    What is the user asking about for the course?? Choose from the following:
    prerequisites, name, credits.
    '''
    return message + prompt_template3

def isCourseAugment(message):
    prompt_template = '''\n
    Is the user asking about a course? Choose from the following:
    yes, no.
    '''
    return message + prompt_template

def RAGTemplate(message):
    prompt_template = '''\n
    You are a chatbot for the University of Massachusetts Lowell. Answer the question as if you a tour guide.
    '''
    return message + prompt_template

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





