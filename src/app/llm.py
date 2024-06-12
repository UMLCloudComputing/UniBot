from umlnow import course, Search, API
import re
import boto3
import json
import os

BEDROCK_ID = os.getenv("BEDROCK_ID")
BEDROCK_KEY = os.getenv("BEDROCK_KEY")

def invoke_llm(input):
    bedrock = boto3.client(
            service_name='bedrock-agent-runtime', 
            region_name='us-east-1',
            aws_access_key_id=BEDROCK_ID,
            aws_secret_access_key=BEDROCK_KEY
            
    )
    if decisionTree(housing(input)) == "yes":
        return bedrock.retrieve_and_generate(
            input={
                'text': RAGTemplate(input)
            },
            retrieveAndGenerateConfiguration={
                'type': 'KNOWLEDGE_BASE',
                'knowledgeBaseConfiguration': {
                    'knowledgeBaseId': "NW82KRCX5W",
                    'modelArn': 'arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-text-premier-v1:0'
                    }
                }
            )["output"]["text"]

    list = course_process(input)
    bedrock = boto3.client(
        service_name='bedrock-runtime', 
        region_name='us-east-1',
        aws_access_key_id=os.getenv("BEDROCK_ID"),
        aws_secret_access_key=os.getenv("BEDROCK_KEY")
        
    )

    truefalse = input+trueorFalse(input)

    modelId = 'amazon.titan-text-lite-v1'
    accept = 'application/json'
    contentType = 'application/json'
    body = json.dumps({
        "inputText": truefalse,
        "textGenerationConfig":{
            "maxTokenCount":512,
            "stopSequences":[],
            "temperature":0,
            "topP":0.9
            }
    })

    response = bedrock.invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)

    response_body = json.loads(response.get('body').read())
    outputText = response_body.get('results')[0].get('outputText')

    if outputText == "yes":
        body = json.dumps({
            "inputText": template_message(input),
            "textGenerationConfig":{
                "maxTokenCount":512,
                "stopSequences":[],
                "temperature":0,
                "topP":0.9
                }
        })
        response = bedrock.invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
        response_body = json.loads(response.get('body').read())
        outputText = response_body.get('results')[0].get('outputText')

        if outputText == "prerequisites":
            return course_info("prereq", list[0])
        elif outputText == "name":
            return course_info("name", list[0])
        elif outputText == "credits":
            return course_info("credits", list[0])

    else:
        body = json.dumps({
            "inputText": input,
            "textGenerationConfig":{
                "maxTokenCount":512,
                "stopSequences":[],
                "temperature":0,
                "topP":0.9
                }
        })
        response = bedrock.invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
        response_body = json.loads(response.get('body').read())
        outputText = response_body.get('results')[0].get('outputText')


    return outputText


def refine_out(message):
    prompt = '''\n
    Refine this output to make it more human readable
    '''
    return message + prompt

def template_message(message):

    prompt_template3 = '''\n
    What is the user asking about for the course?? Choose from the following:
    prerequisites, name, credits.
    '''
    return message + prompt_template3

def trueorFalse(message):
    prompt_template = '''\n
    Is the user asking about a course? Choose from the following:
    yes, no.
    '''
    return message + prompt_template



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

def decisionTree(message):

    bedrock = boto3.client(
        service_name='bedrock-runtime', 
        region_name='us-east-1',
        aws_access_key_id=BEDROCK_ID,
        aws_secret_access_key=BEDROCK_KEY
            
    )

    modelId = 'amazon.titan-text-premier-v1:0'
    accept = 'application/json'
    contentType = 'application/json'
    body = json.dumps({
        "inputText": message,
        "textGenerationConfig":{
            "maxTokenCount":512,
            "stopSequences":[],
            "temperature":0,
            "topP":0.9
            }
    })

    response = bedrock.invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)

    response_body = json.loads(response.get('body').read())
    outputText = response_body.get('results')[0].get('outputText')
    print(outputText)
    return outputText


def retrieveAndGenerate(input, kbId):
    bedrock = boto3.client(
            service_name='bedrock-agent-runtime', 
            region_name='us-east-1',
            aws_access_key_id=BEDROCK_ID,
            aws_secret_access_key=BEDROCK_KEY
            
    )

    if decisionTree(housing(input)) == "yes":
        

        return bedrock.retrieve_and_generate(
            input={
                'text': RAGTemplate(input)
            },
            retrieveAndGenerateConfiguration={
                'type': 'KNOWLEDGE_BASE',
                'knowledgeBaseConfiguration': {
                    'knowledgeBaseId': kbId,
                    'modelArn': 'arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-text-premier-v1:0'
                    }
                }
            )["output"]["text"]

def housing(message):
    prompt_template = '''\n
    Is this statement asking about housing or living somewhere? Choose from the following:
    yes, no.
    '''
    return message + prompt_template

def RAGTemplate(message):
    prompt_template = '''\n
    You are a chatbot for the University of Massachusetts Lowell. Answer the question as if you a tour guide.
    '''
    return message + prompt_template




