---
sidebar_position: 2
---

## 🚀 Setting up.

### Dependencies

You need the following tools:
- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- [Node.JS](https://github.com/nvm-sh/nvm)
- Python `sudo apt install python3`
- AWS CDK `npm install -g aws-cdk`

Then run
`npm install`
`pip install -r requirements.txt`

### Create your dotenv file

1. Clone the repository through `git clone https://github.com/UMLCloudComputing/UniBot`
2. Create an `.env` file with the following variables. You will be needing these in the following steps.
```
APP_NAME=

PINECONE_URL =
PINECONE_API_KEY =

DISCORD_TOKEN=
DISCORD_ID=
DISCORD_PUBLIC_KEY=
```
3. Set your `APP_NAME` to anything you want. However it must be unique and will be used to identify your deployment.
4. Run `cdk bootstrap` to initialize your CDK environment. This will create a CloudFormation stack in your AWS account.





