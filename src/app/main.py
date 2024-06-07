import os
import requests
import boto3
import json
import logging
from flask import Flask, jsonify, request
from mangum import Mangum
from asgiref.wsgi import WsgiToAsgi
from discord_interactions import verify_key_decorator
from botocore.exceptions import ClientError

DISCORD_PUBLIC_KEY = os.environ.get("DISCORD_PUBLIC_KEY")

# Default Parameters for the model
MODEL_ID = "amazon.titan-text-lite-v1"
MAX_TOKEN_COUNT = 512
TEMPERATURE = 0.7
TOP_P = 0.9
STOP_SEQUENCES = []

app = Flask(__name__)
asgi_app = WsgiToAsgi(app)
handler = Mangum(asgi_app)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@app.route("/", methods=["POST"])
async def interactions():
    print(f"👉 Request: {request.json}")
    raw_request = request.json
    return interact(raw_request)


@verify_key_decorator(DISCORD_PUBLIC_KEY)
def interact(raw_request):
    if raw_request["type"] == 1:  # PING
        response_data = {"type": 1}  # PONG
    else:
        data = raw_request["data"]
        command_name = data["name"]

        if command_name == "hello":
            message_content = "Hello there!"
        elif command_name == "echo":
            original_message = data["options"][0]["value"]
            message_content = f"Echoing: {original_message}"
        elif command_name == "chat":
            original_message = data["options"][0]["value"]
            message_content = f"Echoing: {original_message}"
        elif command_name == "weather":
            message_content = weather()

        response_data = {
            "type": 4,
            "data": {"content": message_content},
        }

    return jsonify(response_data)


if __name__ == "__main__":
    app.run(debug=True)

# You can define dedicated functions for commands as well

def weather():
    response = requests.get('https://api.weather.gov/gridpoints/BOX/74,59/forecast')
    data = response.json()
    forecast = data['properties']['periods'][0]
    return f"Weather in Lowell, MA: {forecast['shortForecast']}, {forecast['temperature']}°{forecast['temperatureUnit']}"


# TODO, handle error responses or add additional verbose mode output
def invokeModel(prompt: str, 
                maxTokenCount = MAX_TOKEN_COUNT, 
                temperature = TEMPERATURE, 
                top_P = TOP_P):
    
    logger.info("Generating text with AWS TT Lite model %s", MODEL_ID)
    
    client = boto3.client("bedrock-runtime", region='us-east-1')
    
    native_request = {
        "inputText": prompt,
        "textGenerationConfig": {
            "maxTokenCount": maxTokenCount,
            "temperature": temperature,
            "stopSequences": STOP_SEQUENCES,
            "topP": top_P
        }
    }

    request = json.dumps(native_request)

    try:
        response = client.invoke_model(modelId = MODEL_ID, body = request)

    except(ClientError, Exception) as e:
        logger.info(f"ERROR: Can't invoke {MODEL_ID}. Reason: {e}")
        exit(1)

    model_reponse = json.loads(response["body"].read())

    response_text = model_reponse["results"][0]["outputText"]
    
    return response_text