import requests
import yaml
from dotenv import load_dotenv
import os
import time
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
APPLICATION_ID = os.getenv('DISCORD_ID')
URL = f"https://discord.com/api/v9/applications/{APPLICATION_ID}/commands"
headers = {"Authorization": f"Bot {TOKEN}", "Content-Type": "application/json"}

def delete():
    dict = requests.get(URL, headers=headers)
    registered_commands = dict.json()
    registered_names = {command["name"] for command in registered_commands}
    registered_table = {command["name"]: command["id"] for command in registered_commands}

    with open("discord_commands.yaml", "r") as file:
        yaml_content = file.read()

    commands = yaml.safe_load(yaml_content)
    local_names = {command.get("name") for command in commands}

    delete_commands = registered_names - local_names

    for command in delete_commands:
        id = registered_table[command]
        requests.delete(f"{URL}/{id}", headers=headers)
        print(f"Deleted {command}")
        time.sleep(2)

def register():
    with open("discord_commands.yaml", "r") as file:
        yaml_content = file.read()

    commands = yaml.safe_load(yaml_content)

    # Send the POST request for each command
    for command in commands:
        response = requests.post(URL, json=command, headers=headers)
        command_name = command["name"]
        print(f"Command {command_name} created: {response.status_code}")
        time.sleep(3)

if __name__ == "__main__":
    delete()
    register()