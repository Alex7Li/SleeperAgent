from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from flaskr import game_logic

app = Flask(__name__)

@app.route('/')
def hello_world():
    print("helo")
    return 'Hello from Flask!'


@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    """Send a dynamic reply to an incoming text message"""
    # Get the message the user sent our Twilio number in lowercase
    body = request.values.get('Body', None).lower()

    resp = MessagingResponse()
    try:
        # caller_ind = callers.index(from_number)
        resp.message("Hi, " + "human" + "!")
    except ValueError:
        # Number is not in the list
        resp.message("You have been added to the game")
        pass

    # Send the response back (to your phone)?
    return str(resp)
