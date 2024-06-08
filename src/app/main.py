import os
import requests
# import course
from umlnow import course, Search, API
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
        elif command_name == "course":
            course_id = data["options"][0]["value"]
            course_op = data["options"][1]["value"]
            if course_op == "name":
                message_content = getCourse(course_id)
            elif course_op == "prereq":
                message_content = getPre(course_id)
            elif course_op == "credits":
                message_content = getCr(course_id)
            else:
                message_content = "Incorrect option"
        elif command_name == "pizza":
            message_content = "PIZZA!"

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

def getCourse(courseID):
    return course.get_course_name(course.get_html_response(course.get_course_url(courseID)))

def getPre(courseID):
    return course.get_course_requirements_text(course.get_html_response(course.get_course_url(courseID)))

def getCr(courseID):
    return course.get_course_credits(course.get_html_response(course.get_course_url(courseID)))