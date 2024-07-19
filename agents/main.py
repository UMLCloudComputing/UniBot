from agent import *
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage Bedrock agents.")
    parser.add_argument("action", choices=["prepare", "delete", "list", "create", "update"], help="Action to perform (prepare, delete, or list agents).")
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
    elif args.action == "update":
        if not args.agentid:
            parser.error("The agent_id argument is required for the update action.")
        if not args.name:
            parser.error("The name argument is required for the update action.")
        
        print(args.agentid)
        print(args.name)
        update_agent(args.agentid, args.name)
