from agent import *
import argparse
from dotenv import *
import os

load_dotenv()

AGENT_ID = os.getenv("AGENT_ID")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage Bedrock agents.")
    parser.add_argument("action", choices=["prepare", "delete", "list", "create", "update", "ciupdate"], help="Action to perform (prepare, delete, or list agents).")
    parser.add_argument("agent_id", nargs='?', help="The ID of the agent to prepare or delete. Not required for listing.")
    parser.add_argument("--name", help="The name of the agent to create.", required=False)
    parser.add_argument("--agentid", help="The ID of the agent to update.", required=False)
    
    args = parser.parse_args()
    
    if args.action == "prepare":
        prepare_agent(args.agent_id)
    elif args.action == "delete":
        delete_agent(args.agent_id)
    elif args.action == "list":
        list_agents()
    elif args.action == "create":
        if not args.name:
            parser.error("The --name argument is required for the create action.")
        create_agent(args.name)

    # Manual CLI update
    elif args.action == "update":
        if not args.agentid:
            parser.error("The agent_id argument is required for the update action.")
        if not args.name:
            parser.error("The name argument is required for the update action.")
        
        print(args.agentid)
        print(args.name)
        update_agent(args.agentid, args.name)

    # This is meant for Github Actions
    elif args.action == "ciupdate":
        bedrock = boto3.client (
            service_name='bedrock-agent', 
            region_name='us-east-1',
            aws_access_key_id=AWS_ID,
            aws_secret_access_key=AWS_KEY
        )
        name = bedrock.get_agent(agentId=AGENT_ID).get('agent').get('agentName')
        update_agent(AGENT_ID, name)

