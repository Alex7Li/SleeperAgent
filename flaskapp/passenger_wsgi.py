import os

from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

from flaskapp import game_logic
from flaskapp import functions

project_root = os.path.dirname(os.path.realpath('__file__'))
template_path = os.path.join(project_root, 'app/templates')
static_path = os.path.join(project_root, 'app/static')
app = Flask(__name__, template_folder=template_path,
            static_folder=static_path)

data = {
    # Example data:
    # game_1_id: {
    #     numbers: [#10010010001, #10010010001],
    #     names: {"Agent India", "Agent Bravo"}},
    # game_2_id: {
    #     numbers: [#10010010001, #10010010001],
    #     names: {"Agent India", "Agent Bravo"}
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
    body = request.values.get('Body', None)
    # Get the number the request was sent from
    from_number = request.form['From']

    if body == "start new game":
        game_logic.end_game()
        game_logic.start_game(from_number)
        return "Started a new game"
    # Start our TwiML response
    resp = MessagingResponse()

    # Determine the right reply for this message
    if body.lower() == 'hello':
        resp.message()
    elif body.lower() == 'bye':
        resp.message("Goodbye")

    return str(resp)


application = app
