---
sidebar_position: 5
---

## 📦 Deploying The Discord Bot

1. Deploy your Discord Bot by running `cdk deploy`.
2. If successful, `cdk deploy` should have this: `DiscordBotLambdaTest.ApiGatewayUrl = <Your API Gateway URL>` in the output.
3. Copy the API Gateway URL and go to your Discord Developer's Portal (discord.dev). Set this as Interactions Endpoint for your Bot.
![image](https://github.com/UMLCloudComputing/rowdybot/assets/136134023/6e0171af-3151-4223-9590-b7d9953aca39)
4. If this fails, try again after a few seconds. Your lambda function needs some time to boot up.

## 👑 Running the Streamlit Application
1. Run the Streamlit application by running `streamlit run src/streamlit.py`.
2. The Streamlit application should be running on `localhost:8501`.