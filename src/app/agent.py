import boto3
import os
# from dotenv import load_dotenv

# load_dotenv()

AWS_ID = os.getenv('AWS_ID')
AWS_KEY = os.getenv('AWS_KEY')

def update_alias():
    bedrock = boto3.client(
        service_name='bedrock-agent', 
        region_name='us-east-1',
        aws_access_key_id=AWS_ID,
        aws_secret_access_key=AWS_KEY
    )

    print(AWS_ID)
    print(AWS_KEY)

    agent_alias_id = os.getenv('AGENT_ALIAS')
    agent_id = os.getenv('AGENT_ID')

    response = bedrock.get_agent_alias(
        agentAliasId=agent_alias_id,
        agentId=agent_id
    )

    update_response = bedrock.update_agent_alias (
        agentAliasId=agent_alias_id,
        agentAliasName=response['agentAlias']['agentAliasName'],
        agentId=agent_id
    )
    print("Successfully updated Agent")