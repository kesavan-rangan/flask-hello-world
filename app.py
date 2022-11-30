from flask import Flask
from flask import request
import requests
import traceback
import json
from azure.storage.blob import BlobClient
import os

app = Flask(__name__)
SAS_URL = os.getenv("AZURE_SAS_URL", "")

@app.route('/')
def hello_world():
    return 'Hello, World!'


def _upload_feedback_json(uuid, json_string):
    sas_url_blob = SAS_URL.format(blob_name=uuid)
    blob_client = BlobClient.from_blob_url(sas_url_blob)
    blob_client.upload_blob(json_string, overwrite=True)


@app.route('/interactive', methods=['POST'])
def slack_interactivity():
    try:
        print("-------Request Headers -------")
        print(request.headers)
        print("-------Request Form -------")
        print(request.form)
        request_body = json.loads(request.form.to_dict().get("payload"))
        if request_body and request_body.get("actions"):
            action_info = request_body.get("actions")[0]
            if action_info.get("action_id") == "jit-feedback-submit":
                jit_ticket_id = action_info.get("value")
                print(request_body)
                response_url = request_body.get("response_url")
                values = request_body.get("state", {}).get("values")
                user_response = {"jit_ticket_id": jit_ticket_id}
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
                _upload_feedback_json(jit_ticket_id, json.dumps(user_response))
                if r.status_code == 200:
                    print("Updated the message")
    except Exception as e:
        message = traceback.format_exc()
        print(message)
    return 'slack interactivity'
