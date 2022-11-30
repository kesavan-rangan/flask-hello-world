from flask import Flask
from flask import request
import traceback

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
        print("-------Request JSON body -------")
        print(request.get_json())
        print("-------Done-------")
    except Exception as e:
        message = traceback.format_exc()
        print(message)
    return 'slack interactivity'
