import requests
import yaml
from dotenv import load_dotenv
import os
import time
load_dotenv()

TOKEN = os.getenv('TOKEN')
APPLICATION_ID = os.getenv('ID')
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

delete()