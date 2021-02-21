import os

from flask import Flask, request, render_template, redirect, url_for
from twilio.twiml.messaging_response import MessagingResponse

project_root = os.path.dirname(os.path.realpath('__file__'))
template_path = os.path.join(project_root, 'app/templates')
static_path = os.path.join(project_root, 'app/static')
app = Flask(__name__, template_folder=template_path, 
static_folder=static_path)

i=0

@app.route('/')
def index():
    return 'Hello from flask'

@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    """Send a dynamic reply to an incoming text message"""
    # Get the message the user sent our Twilio number
    body = request.values.get('Body', None)
    global i
    # Start our TwiML response
    resp = MessagingResponse()

    # Determine the right reply for this message
    if body.lower() == 'hello':
        i+=1
        resp.message(str(i))
    elif body.lower() == 'bye':
        resp.message("Goodbye")
    
    return str(resp)


application = app
