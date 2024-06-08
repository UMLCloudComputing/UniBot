import os
import requests
# import course
import course
from flask import Flask, jsonify, request
from mangum import Mangum
from asgiref.wsgi import WsgiToAsgi
from discord_interactions import verify_key_decorator


DISCORD_PUBLIC_KEY = os.environ.get("DISCORD_PUBLIC_KEY")

app = Flask(__name__)
asgi_app = WsgiToAsgi(app)
handler = Mangum(asgi_app)


@app.route("/", methods=["POST"])
async def interactions():
    print(f"👉 Request: {request.json}")
    raw_request = request.json
    return interact(raw_request)


@verify_key_decorator(DISCORD_PUBLIC_KEY)
def interact(raw_request):

    # Let discord know that this bot is alive
    if raw_request["type"] == 1:  # PING
        response_data = {"type": 1}  # PONG
    
    # Discord sends a request based on the slash command entered
    # This will intepret the request
    else:
        # Auxiliary Command Data. Used to extract arguments
        data = raw_request["data"]

        # The command being execute
        command_name = data["name"]

        # Command /hello
        if command_name == "hello":
            # message_content is the response to the user
            message_content = "Hello there!"

        # Command /echo
        elif command_name == "echo":
            original_message = data["options"][0]["value"]
            message_content = f"Echoing: {original_message}"

        # Command /chat [arg1: message]
        # Will Integrate LLM later
        elif command_name == "chat":
            # The first argument
            original_message = data["options"][0]["value"]
            message_content = f"It's great that you're saying that: {original_message}"

        # Command /weather [arg1: city]
        # Gets the weather in just Lowell for now. Ignores the argument for city
        elif command_name == "weather":
            message_content = weather()

        # Command /course [arg1: COURSE ID] [arg2: option]
        elif command_name == "course":
            course_id = data["options"][0]["value"]
            course_op = data["options"][1]["value"]
            message_content = course.course_info(course_op, course_id)

        # Command /pizza
        # Fun little command that prints pizza.
        elif command_name == "pizza":
            message_content = "PIZZA! 🍕🍕🍕🍕🍕"

        # Fire back a response to the user by making a json request
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

