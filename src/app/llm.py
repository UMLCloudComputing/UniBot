import boto3
import json
# from dotenv import load_dotenv
import os
import requests

# load_dotenv()

def invoke_llm(input, token):
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

    print(token)

    url = f"https://discord.com/api/webhooks/1248706794008870967/{token}/messages/@original"

    # JSON data to send with the request
    data = {
        "content": outputText
    }

    # Send the PATCH request
    response = requests.patch(url, json=data)