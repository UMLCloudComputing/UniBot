---
sidebar_position: 6
---

## 👉 Commands

### Registering Commands
1. Create an `.env` file in the root directory of the project. Do not upload this file to github, it contains secrets.
2. Make sure these environmental variables are in your `.env` file.
   1. `TOKEN=<your discord bot token>`
   2. `ID=<your discord bot ID>`
3. Enter new commands in this format, with each one on a new line in the file `commands/discord_commands.yaml`
```
- name: <name of your command>
  description: <command description>
  options:
    - name: <parameter 1>
      description: <parameter description>
      type: 3 # string
      required: true
    - name: <parameter 2>
      description: <parameter 2 description>
      type: 3 # string
      required: true
```
1. From your root directory, run `python3 register_commands.py`
2. You should receive the status `201` or `200` printing out in your terminal.

### Adding Command Functionality
1. Commands can be defined in the file `src/app/main.py`.
2. This bot uses the Discord Interactions API, which is a REST API. When a user executes a slash command, Discord will make an API request to the endpoint you specify in the Discord Developer Portal
3. The full structure of the Interactions API can be found in the [Discord API Documentation](https://discord.com/developers/docs/interactions/slash-commands).
4. For the purposes of our bot, we will turn the JSON request into a Python object and then use the `request['data']['name']` field to determine which command to run.