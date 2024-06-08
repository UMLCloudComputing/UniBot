import boto3
import json
# from dotenv import load_dotenv
import os

# load_dotenv()

def invoke_llm(input):
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

print(invoke_llm("What is the equation for gravitational acceleration of a pendulum"))