# Rowdy the Riverbot
Discord Bot, to answers all your questions about UML.

## Contributing
Commit messages should follow this specification https://www.conventionalcommits.org/en/v1.0.0/

## How it works
As of now, the command model with the bot is asynchronous. 

Upon executing a slash command, discord will call the url specified in "Interaction Endpoints URL" (which can be specified in the discord app development portal). This url will be the Lambda Function URL, that will be printed in the command line when you run `cdk deploy`.The result of discord calling this URL will execute the lambda function. When the bot is not in use, the lambda function will not run, significantly saving costs compared to an EC2 instance.

`src/app/main.py` will interpret the command and return a result back to the user.

## Setting up.
1. Install everything listed in the dependencies section.
2. Clone the repository
3. Create an IAM user with the permissions to access lambda functions and cloud formation.
4. Run `aws configure` to setup your AWS credentials.
5. Run `cdk bootstrap` to setup the cdk project.
6. In a CI/CD environment, you should set the environmental variable `DISCORD_PUBLIC_KEY` to the public key of your discord bot, which can be found in the developer portal.
7. Alternatively go to the file `lib/discord-bot-lambda-stack.ts` and hardcode public key of your discord bot.

# Command Registration
1. Create an `.env` file in the root directory of the project. Do not upload this file to github, it contains secrets.
2. Set these two variables in the file
   1. `TOKEN=<your discord bot token>`
   2. `ID=<your discord bot ID>`
3. Enter new commands in this format, with each one on a new line in the file `commands/discord_commands.yaml`
4. If you want CI/CD to do this for you, please set these environmetal variables in your CI/CD environment.

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
4. From your root directory, run `python3 register_commands.py`
5. You should receive the status `201` or `200` printing out in your terminal.


# Command definition
1. Commands can be defined in the file `src/app/main.py`
2. You can register commands in the `interact` function by adding more `elif` statements. 
   1. The parameters of the command that are received from the user is in encoded in the variable `data`. The statement `data["options"][n]["value"]` will extract the argument `n`.   
   2. The message that the bot returns to the user is specified in the string variable `message_content`. It is crucial that `message_content` is a string.

# Deploying
1. Deploy to lambda by running `cdk deploy`.
2. If `cdk deploy` fails due to insufficient privileges to run docker, type `sudo cdk deploy`. If that doesn't work, type `sudo -i` to become root, `cd` back to the project root and run `cdk deploy` again.
3. If you are deploying this using CI/CD methods, you will most likely need to rerun what you ran in the setup phase, **especially** `cdk bootstrap`.
4. If successful, `cdk deploy` should have this: `DiscordBotLambdaStack.FunctionUrl = <your lambda function url>` in the output.
5. Copy the lambda function URL and go to the discord developer's portal. Set this as Interactions Endpoint for your Bot.

## Dependencies
AWS CLI
AWS CDK `npm install -g aws-cdk`
Flask `pip install flask`
Discord Interactions `pip install discord-interactions`
pyyaml `pip install pyyaml`
requests `pip install requests`

## Technologies:
1. AWS Lambda
2. AWS CDK
3. AWS Cloudformation
4. AWS Bedrock
5. Discord Interactions

## Invite link
[Invite Link](https://discord.com/oauth2/authorize?client_id=1241285489969856514&permissions=8&scope=bot%20applications.commands)

