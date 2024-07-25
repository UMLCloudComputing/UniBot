from umlnow import course, Search, API
import re
import course
import boto3
import json
import os

if __name__ == "__main__":
    from dotenv import *
    load_dotenv()

AWS_ID = os.getenv("AWS_ID")
AWS_KEY = os.getenv("AWS_KEY")
MAX_TOKEN = os.getenv("MAX_TOKEN", 256)
AGENT_ALIAS = os.getenv("AGENT_ALIAS")
AGENT_ID = os.getenv("AGENT_ID")

def invoke_llm(input, userID):
    return LLMTitanPremier(input, userID)

# Call the Titan Premier Model (RAG Capabilities)
def LLMTitanPremier(input, userID):
    bedrock = boto3.client(
        service_name='bedrock-agent-runtime', 
        region_name='us-east-1',
        aws_access_key_id=AWS_ID,
        aws_secret_access_key=AWS_KEY
            
    )   
    bedrockObj = bedrock.invoke_agent (
        agentAliasId=AGENT_ALIAS,
        agentId=AGENT_ID,
        inputText=input,
        sessionId=userID
    )

    print(bedrockObj)

    eventStream = bedrockObj['completion']
    url = ""

    for event in eventStream:
        print(event)
        if 'chunk' in event:
            data = event['chunk']['bytes'].decode('utf-8')
            returnString = data
        if 'attribution' in event['chunk']:
            print(event['chunk']['attribution'])
            for citations in event['chunk']['attribution']['citations']:
                for references in citations['retrievedReferences']:
                    print(f"Metadata\n{references}")
                    url = references.get('metadata').get('url')

    return f"{returnString}\n {url}"





