from umlnow import course, Search, API
import re
import course
import boto3
import json
import os

BEDROCK_ID = os.getenv("BEDROCK_ID")
BEDROCK_KEY = os.getenv("BEDROCK_KEY")
S3_ID = os.getenv("S3_ID")
S3_KEY = os.getenv("S3_KEY")
KNOWLEDGE = os.getenv("KNOWLEDGE_BASE_ID")
MAX_TOKEN = os.getenv("MAX_TOKEN", 256)

def invoke_llm(input):
    # Check if the user is asking about a course
    isCourse = LLMTitanLite(isCourseAugment(input))

    # Course specific question about UML
    if isCourse == "yes":
        # Regex that filters out course IDs
        list = course_process(input)

        # Decide what user is asking about for courses
        outputText = LLMTitanLite(UMLNowAugment(input))

        match outputText:
            case "prerequisites": return course.course_info("prereq", list[0])
            case "name": return course.course_info("name", list[0])
            case "credits": return course.course_info("credits", list[0])

    isCost = LLMTitanLite(cost(input))
    print(isCost)

    if isCost == "yes":
        return LLMTitanPremier(input, "QP7VVBWZY8")

    # General question about UML
    else:
        return LLMTitanPremier(RAGTemplate(input), KNOWLEDGE)

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
            "maxTokenCount": MAX_TOKEN,
            "stopSequences":[],
            "temperature":0,
            "topP":0.9
            }
    })

 
    response = bedrock.invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
    response_body = json.loads(response.get('body').read())
    return response_body.get('results')[0].get('outputText')

# Call the Titan Premier Model (RAG Capabilities)
def LLMTitanPremier(input, knowledge):
    bedrock = boto3.client(
        service_name='bedrock-agent-runtime', 
        region_name='us-east-1',
        aws_access_key_id=BEDROCK_ID,
        aws_secret_access_key=BEDROCK_KEY
            
    )   
    bedrockObj = bedrock.retrieve_and_generate(
        input={
            'text': input
        },
        retrieveAndGenerateConfiguration={
            'type': 'KNOWLEDGE_BASE',
            'knowledgeBaseConfiguration': {
                'knowledgeBaseId': knowledge,
                'modelArn': 'arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-text-premier-v1:0'
                }
            }
        )
    
    returnString = bedrockObj['output']['text']

    for citation in bedrockObj['citations']:
        for reference in citation['retrievedReferences']:
            uri = reference['location']['s3Location']['uri']

    filename = extract_filename(uri)
    metadata = filename + ".json"

    print(metadata)

    s3 = boto3.client('s3', aws_access_key_id=S3_ID, aws_secret_access_key=S3_KEY)
    obj = s3.get_object(Bucket='rowdysources', Key=metadata)
    data = json.loads(obj['Body'].read().decode('utf-8'))

    return returnString + "\n" + "Citations: " + data['url']

def extract_filename(s3_uri):
    # Regex pattern to match the filename at the end of the URI
    pattern = r'[^/]+$'
    # Search for the pattern in the URI and extract the filename
    match = re.search(pattern, s3_uri)
    if match:
        return match.group()
    else:
        return None

# Augmented Prompts

def cost(message):
    prompt_template = '''\n
    Does the statement above ask about cost? Choose from the following:
    yes, no
    '''
    return message + prompt_template

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

    When the user asks about housing, you should provide information about the residence hall, and its price.
    
    If you don't know the answer to a question, you should say "Can you clarify your question?".
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





