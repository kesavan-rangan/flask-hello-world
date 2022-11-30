from flask import Flask
from flask import request
import requests
import traceback
import json

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/interactive', methods=['POST'])
def slack_interactivity():
    try:
        print("-------Request ARGS -------")
        print(request.args)
        print("-------Request Headers -------")
        print(request.headers)
        print("-------Request Form -------")
        print(request.form)
        request_body = request.get_data().decode()
        print(request_body)
        print("-------Request JSON body -------")
        print(request.get_json())
        print("-------Done-------")
        if request_body and request_body.get("actions"):
            action_required = False
            for action in request_body.get("actions"):
                if action.get("action_id") == "jit-feedback-submit":
                    action_required = True
            if action_required:
                response_url = request_body.get("response_url")
                values = request_body.get("state", {}).get("values")
                user_response = {}
                if values:
                    for key, value in values.items():
                        for sub_key, sub_value in value.items():
                            if sub_value.get("type") == "static_select":
                                user_response[sub_key] = sub_value.get("selected_option", {}).get("value")
                            elif sub_value.get("type") == "plain_text_input":
                                user_response[sub_key] = sub_value.get("value")

                user_response["user"] = request_body.get("user", {})
                user_response["message_timestamp"] = request_body.get("container", {}).get("message_ts")
                user_response["trigger_id"] = request_body.get("trigger_id")
                print(f"Response received - {json.dumps(user_response)}")
                slack_response = {
                    "replace_original": "true",
                    "text": "Thanks for your valuable feedback!"
                }
                r = requests.post(response_url, data=json.dumps(slack_response))
                if r.status_code == 200:
                    print("Updated the message")
    except Exception as e:
        message = traceback.format_exc()
        print(message)
    return 'slack interactivity'
