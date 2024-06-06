<div align="center">

[![Contributors](https://img.shields.io/github/contributors/UMLCloudComputing/rowdybot.svg?style=for-the-badge)](https://github.com/UMLCloudComputing/rowdybot/graphs/contributors)
[![Forks](https://img.shields.io/github/forks/UMLCloudComputing/rowdybot.svg?style=for-the-badge)](https://github.com/UMLCloudComputing/rowdybot/network/members)
[![Stargazers](https://img.shields.io/github/stars/UMLCloudComputing/rowdybot.svg?style=for-the-badge)](https://github.com/UMLCloudComputing/rowdybot/stargazers)
[![Issues](https://img.shields.io/github/issues/UMLCloudComputing/rowdybot.svg?style=for-the-badge)](https://github.com/UMLCloudComputing/rowdybot/issues)
[![MIT License](https://img.shields.io/github/license/UMLCloudComputing/rowdybot.svg?style=for-the-badge)](https://github.com/UMLCloudComputing/rowdybot/blob/master/LICENSE)

# 📘 About
A Discord Bot to answers all your questions about UML! Has LLM integration to respond to a wide variety of questions.

## 🎉 Acknowledgments

Many thanks to the [UMass Lowell Cloud Computing Club](https://umasslowellclubs.campuslabs.com/engage/organization/cloudcomputingclub) members, our faculty advisor [Dr. Johannes Weis](https://www.uml.edu/sciences/computer-science/people/weis-johannes.aspx), and the [UMass Lowell Computer Science Department](https://www.uml.edu/Sciences/computer-science/) for their support and guidance.
[![Contributors](https://contributors-img.web.app/image?repo=UMLCloudComputing/UniPath.io)](https://github.com/UMLCloudComputing/UniPath.io/graphs/contributors)


## 👨‍💻 Contributing

Contributions are what make the open-source community an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

<details>
<summary>Creating a New Branch and Making a Pull Request</summary>

Follow these steps to contribute to the project with a new feature or bug fix:

### Step 1: Create a New Branch
Before starting your work, ensure you're on the `main` branch and that it's up to date.

```sh
git checkout main
git pull origin main
```

Create a new branch for your feature or bug fix. Follow a naming convention like `feature/<feature-name>` or `bugfix/<bug-name>`.

```sh
git checkout -b feature/my-new-feature
# or
git checkout -b bugfix/my-bug-fix
```

### Step 2: Make Your Changes
Implement your feature or fix the bug in your branch. Commit your changes using clear, concise, and conventional commit messages following the guidelines at [conventionalcommits.org](https://www.conventionalcommits.org).

```sh
git add .
git commit -m "feat: add my new feature"
# or
git commit -m "fix: correct a bug"
```

Optionally, if you assigned yourself an issue, you can automatically create and link a branch using the GitHub UI. Click on the "Create a branch" button and select the option to create a new branch for the issue.

### Step 3: Push Your Changes
Push your changes to the repository.

```sh
git push origin feature/my-new-feature
# or
git push origin bugfix/my-bug-fix
```

#### Style Guide
- Use clear, concise, and conventional commit messages. Commit messages should follow this specification https://www.conventionalcommits.org/en/v1.0.0/
- Follow the best software development practices and write clean, maintainable code.
- For ReactJS, follow this style guide: <https://dev.to/abrahamlawson/react-style-guide-24pp>. Except use indendantation of 4 spaces instead of 2.

### Step 4: Create a Pull Request
Go to the GitHub repository page and click on the "Pull request" button. Select your branch and provide a detailed description of your changes. Explain why your changes should be merged into the main branch.

### Step 5: Review and Merge
Wait for the project maintainers to review your pull request. They may request changes. Once your pull request is approved, a project maintainer will merge it into the main branch.

Thank you for your contribution!

</details>

## ⭐ How it works
As of now, the command model with the bot is asynchronous. 

Upon executing a slash command, discord will call the url specified in "Interaction Endpoints URL" (which can be specified in the discord app development portal). This url will be the Lambda Function URL, that will be printed in the command line when you run `cdk deploy`.The result of discord calling this URL will execute the lambda function. When the bot is not in use, the lambda function will not run, significantly saving costs compared to an EC2 instance.

`src/app/main.py` will interpret the command and return a result back to the user.

## 🚀 Setting up.
1. Install everything listed in the dependencies section.
2. Clone the repository
3. Create an IAM user with the permissions to access lambda functions and cloud formation.
4. Run `aws configure` to setup your AWS credentials.
5. Run `cdk bootstrap` to setup the cdk project.
6. In a CI/CD environment, you should set the environmental variable `DISCORD_PUBLIC_KEY` to the public key of your discord bot, which can be found in the developer portal.
7. Alternatively go to the file `lib/discord-bot-lambda-stack.ts` and hardcode public key of your discord bot.

![image](https://github.com/UMLCloudComputing/rowdybot/assets/136134023/595f713f-c415-4b1d-937f-86929e0c5e00)

## ⚙ Command Registration
1. Create an `.env` file in the root directory of the project. Do not upload this file to github, it contains secrets.
2. Set these two variables in the file
   1. `TOKEN=<your discord bot token>`
   2. `ID=<your discord bot ID>`
3. Enter new commands in this format, with each one on a new line in the file `commands/discord_commands.yaml`
4. If you want CI/CD to do this for you, please set these environmental variables in your CI/CD environment.

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


## 👉 Command definition
1. Commands can be defined in the file `src/app/main.py`
2. You can register commands in the `interact` function by adding more `elif` statements. 
   1. The parameters of the command that are received from the user is in encoded in the variable `data`. The statement `data["options"][n]["value"]` will extract the argument `n`.   
   2. The message that the bot returns to the user is specified in the string variable `message_content`. It is crucial that `message_content` is a string.

## 📦 Deploying
1. Deploy to lambda by running `cdk deploy`.
2. If `cdk deploy` fails due to insufficient privileges to run docker, type `sudo cdk deploy`. If that doesn't work, type `sudo -i` to become root, `cd` back to the project root and run `cdk deploy` again.
3. If you are deploying this using CI/CD methods, you will most likely need to rerun what you ran in the setup phase, **especially** `cdk bootstrap`.
4. If successful, `cdk deploy` should have this: `DiscordBotLambdaStack.FunctionUrl = <your lambda function url>` in the output.
5. Copy the lambda function URL and go to the discord developer's portal. Set this as Interactions Endpoint for your Bot.

## 🤯 Dependencies
AWS CLI
AWS CDK `npm install -g aws-cdk`
Flask `pip install flask`
Discord Interactions `pip install discord-interactions`
pyyaml `pip install pyyaml`
requests `pip install requests`

## 🔥 Technologies:
1. AWS Lambda
2. AWS CDK
3. AWS Cloudformation
4. AWS Bedrock
5. Discord Interactions

## 🎉 Invite link
[Invite Link](https://discord.com/oauth2/authorize?client_id=1241285489969856514&permissions=8&scope=bot%20applications.commands)

