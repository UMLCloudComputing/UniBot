import boto3
import os
from dotenv import load_dotenv
import json
from botocore.exceptions import ClientError
from logging import *
import random
import string
import time

load_dotenv()

AWS_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

# Prompts
prompt = '''System: A chat between a curious User and an artificial intelligence Bot. The Bot gives helpful, detailed, and polite answers to the User's questions. In this session, the model has access to external functionalities.
To assist the user, you can reply to the user or invoke an action. Only invoke actions if relevant to the user request.
$instruction$

The following actions are available:$tools$
Model Instructions:
$model_instructions$
$conversation_history$
User: $question$
$thought$ $bot_response$
'''

kbgeneration = '''A chat between a curious User and an artificial intelligence Bot. The Bot gives helpful, detailed, and polite answers to the User's questions.

In this session, the model has access to search results and a user's question, your job is to answer the user's question using only information from the search results.

Model Instructions:
- You should provide concise answer to simple questions when the answer is directly contained in search results, but when comes to yes/no question, provide some details.
- In case the question requires multi-hop reasoning, you should find relevant information from search results and summarize the answer based on relevant information with logical reasoning.
- If the search results do not contain information that can answer the question, please state that you could not find an exact answer to the question, and if search results are completely irrelevant, say that you could not find an exact answer, then summarize search results.
- Remember to add a citation to the end of your response using markers like %[1]%, %[2]%, %[3]%, etc for the corresponding passage supports the response.
- DO NOT USE INFORMATION THAT IS NOT IN SEARCH RESULTS!

User: $query$ Bot:
Resources: Search Results: $search_results$ Bot:
'''

with open('instructions.txt', 'r') as file:
    # Step 2: Read the contents
    instruction = file.read()

def generate_random_string(length):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

# random_string = generate_random_string(10)
# print(random_string)

def create_agent_role(model_id, policy_name):
    role_name = f"AmazonBedrockExecutionRoleForAgents_{generate_random_string(10)}"
    model_arn = f"arn:aws:bedrock:us-east-1::foundation-model/{model_id}*"

    print("Creating an an execution role for the agent...")

    iam_resource=boto3.resource(
        service_name="iam",
        region_name='us-east-1',
        aws_access_key_id=AWS_ID,
        aws_secret_access_key=AWS_KEY           
    )

    try:
        role = iam_resource.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(
                {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {"Service": "bedrock.amazonaws.com"},
                            "Action": "sts:AssumeRole",
                        }
                    ],
                }
            ),
        )

        role.Policy(policy_name).put(
            PolicyDocument=json.dumps(
                {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Action": "bedrock:InvokeModel",
                            "Resource": model_arn,
                        },
                        {
                            "Effect": "Allow",
                            "Action": "bedrock:ListAgentAliases",
                            "Resource": "*"
                        }
                    ],
                }
            )
        )
    except ClientError as e:
        print(f"Couldn't create role {role_name}. Here's why: {e}")
        raise

    sts_client = boto3.client(
        service_name='sts', 
        region_name='us-east-1',
        aws_access_key_id=AWS_ID,
        aws_secret_access_key=AWS_KEY
    )
    
    caller_identity = sts_client.get_caller_identity()
    account_id = caller_identity['Account']

    returnStr = f"arn:aws:iam::{account_id}:role/{role_name}"
    return returnStr

# Create Amazon Bedrock Agent
def create_agent(agent_name):
    bedrock = boto3.client(
        service_name='bedrock-agent', 
        region_name='us-east-1',
        aws_access_key_id=AWS_ID,
        aws_secret_access_key=AWS_KEY
    )

    response = bedrock.create_agent(
        agentName=agent_name,
        agentResourceRoleArn=create_agent_role('amazon.titan-text-premier-v1:0', 'AmazonBedrockExecutionRoleForAgents'),
        description='Testing',
        foundationModel='amazon.titan-text-premier-v1:0',
        idleSessionTTLInSeconds=123,
        instruction=instruction,
        promptOverrideConfiguration={
            'promptConfigurations': [
                {
                    'basePromptTemplate': prompt,
                    'inferenceConfiguration': {
                        'maximumLength': 256,
                        'temperature': 0, 
                        'topK': 123,
                        'topP': 0.1
                    },
                    'parserMode': 'DEFAULT',
                    'promptCreationMode': 'OVERRIDDEN',
                    'promptState': 'ENABLED',
                    'promptType': 'ORCHESTRATION'
                },

                {
                    'basePromptTemplate': prompt,
                    'inferenceConfiguration': {
                        'maximumLength': 256,
                        'temperature': 0,
                        'topK': 123,
                        'topP': 0.1
                    },
                    'parserMode': 'DEFAULT',
                    'promptCreationMode': 'OVERRIDDEN',
                    'promptState': 'ENABLED',
                    'promptType': 'KNOWLEDGE_BASE_RESPONSE_GENERATION'
                }
            ]
        },
        tags={
            'string': 'string'
        }
    )

    time.sleep(5)
    prepare_agent(response['agent']['agentId'])

    return f'''Please add this to your .env file\nAGENT_ID = {response['agent']['agentId']}\n
Go to this link https://us-east-1.console.aws.amazon.com/bedrock/home?region=us-east-1#/agents/{response['agent']['agentId']}/ '''

def list_agents():
    client = boto3.client(
        service_name='bedrock-agent', 
        region_name='us-east-1',
        aws_access_key_id=AWS_ID,
        aws_secret_access_key=AWS_KEY
    )
    response = client.list_agents(
        maxResults=123,
    )

    for summary in response['agentSummaries']:
        print(f"Agent Name: {summary['agentName']}, Agent ID: {summary['agentId']}")

def prepare_agent(agent_id):
    bedrock = boto3.client(
        service_name='bedrock-agent', 
        region_name='us-east-1',
        aws_access_key_id=AWS_ID,
        aws_secret_access_key=AWS_KEY
    )

    preparation = bedrock.prepare_agent(
        agentId=agent_id
    )

def update_agent(agent_id, agent_name):
    bedrock = boto3.client(
        service_name='bedrock-agent', 
        region_name='us-east-1',
        aws_access_key_id=AWS_ID,
        aws_secret_access_key=AWS_KEY
    )

    response = bedrock.update_agent(
        agentId=agent_id,
        agentName=agent_name,
        agentResourceRoleArn=create_agent_role('amazon.titan-text-premier-v1:0', 'AmazonBedrockExecutionRoleForAgents'),
        description='Testing',
        foundationModel='amazon.titan-text-premier-v1:0',
        idleSessionTTLInSeconds=123,
        instruction=instruction,
        promptOverrideConfiguration={
            'promptConfigurations': [
                {
                    'basePromptTemplate': prompt,
                    'inferenceConfiguration': {
                        'maximumLength': 256,
                        'temperature': 0, 
                        'topK': 123,
                        'topP': 0.1
                    },
                    'parserMode': 'DEFAULT',
                    'promptCreationMode': 'OVERRIDDEN',
                    'promptState': 'ENABLED',
                    'promptType': 'ORCHESTRATION'
                },

                {
                    'basePromptTemplate': prompt,
                    'inferenceConfiguration': {
                        'maximumLength': 256,
                        'temperature': 0,
                        'topK': 123,
                        'topP': 0.1
                    },
                    'parserMode': 'DEFAULT',
                    'promptCreationMode': 'OVERRIDDEN',
                    'promptState': 'ENABLED',
                    'promptType': 'KNOWLEDGE_BASE_RESPONSE_GENERATION'
                }
            ]
        },
    )


def delete_agent():
    list_agents()

    agent_id = input("Enter the agent ID you want to delete: ")

    bedrock = boto3.client(
        service_name='bedrock-agent', 
        region_name='us-east-1',
        aws_access_key_id=AWS_ID,
        aws_secret_access_key=AWS_KEY
    )

    response = bedrock.delete_agent(
        agentId=agent_id,
        skipResourceInUseCheck=True
    )

def list_agent_aliases(agentId):
    bedrock = boto3.client(
        service_name='bedrock-agent', 
        region_name='us-east-1',
        aws_access_key_id=AWS_ID,
        aws_secret_access_key=AWS_KEY
    )

    response = bedrock.list_agent_aliases(
        agentId=agentId,
        maxResults=123
    )

    for summary in response['agentAliasSummaries']:
        print(f"Alias Name: {summary['agentAliasName']}, Alias ID: {summary['agentAliasId']}")

def create_alias(agentId):
    pass

if __name__ == "__main__":
    list_agent_aliases("RNFMM5CPB5")