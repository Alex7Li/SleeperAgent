import os

from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

import game_logic

project_root = os.path.dirname(os.path.realpath('__file__'))
template_path = os.path.join(project_root, 'app/templates')
static_path = os.path.join(project_root, 'app/static')
app = Flask(__name__, template_folder=template_path,
            static_folder=static_path)

data = {
    # Example data:
    # game_1_id: {
    #     'numbers': ["#10010010001", "#10010010001"],
    #     'names': ["Agent India", "Agent Bravo"]},
    #     'roles': [0, 1, 0],
    #     'current_phase: 0->setup, 1->doing button, 2->doing espionage, 3->doing mission, 4->doing execution
    # game_2_id: {
    #     'numbers': ["#10010010001", "#10010010001"],
    #     'names': ["Agent India", "Agent Bravo"]
    #     'current_phase: 2'
    # },
}


@app.route('/')
def index():
    return "Text this number to play 720-399-8395"


@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    """Send a dynamic reply to an incoming text message"""
    global data
    # Get the message the user sent our Twilio number
    body = request.values.get('Body', None).lower()
    # Get the number the request was sent from
    from_number = request.form['From'].lower()

    response = game_logic.determine_response(data, from_number, body)
    # Text back the response
    if response is not None:
        return str(MessagingResponse(response))



application = app