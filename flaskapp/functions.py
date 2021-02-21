import numpy as np
import os
from twilio.rest import Client
import random

# checks to the left and right and ra
def espionage(numbers,roles):
    roles.append(roles[0])
    
    texts = []
    right = np.random.randint(0,2)
    for c in range(len(numbers)):
        if right:
            if roles[c+1]:
                texts.append("CODE RED: Espionage Detected")
            else:
                texts.append("ALL CLEAR: Espionage NOT Detected")
                
        else:
            if roles[c-1]:
                texts.append("CODE RED: Espionage Detected")
            else:
                texts.append("ALL CLEAR: Espionage NOT Detected")
                
    return numbers,texts

# set up the game with roles and phone numbers, input number of people
def SetupGameState(n):

    # 0 = good, 1 = bad
    roles = np.zeros(n)
    roles[random.randint(0,n-1)] = 1
    return roles

# creates names from how many are needed
def NameGenerator(num_names):
    list_names = ['Alpha','Bravo','Charlie','Delta','Echo',
                  'Foxtrot','Golf','Hotel','India','Juliet',
                  'Kilo','Lima','Mike','November','Oscar','Papa',
                  'Quebec','Romeo','Sierra','Tango','Uniform',
                  'Victor','Whiskey','X-ray','Yankee','Zulu']

    return_names = []
    for i in range(num_names):
        name = random.choice(list_names)
        return_names.append("Agent "+name)
        list_names.remove(name)
            
    return return_names

# enlists users for new game
def collect_users_start(numbers):
    from_number = request.values.get('From', None)
    if body.lower()=="enlist me":
        numbers.append(from_number)
    else:
        resp = MessagingResponse()
        resp.message('Permission Denied, text "Enlist Me" to continue')
        
    return numbers


# send any text to n number of numbers
def send_text(numbers,text):

    # Find these values at https://twilio.com/user/account
    # To set up environmental variables, see http://twil.io/secure
    account_sid = "AC3814bc45f99ac5af25d5f45c61cdf33d"
    auth_token = "2de3933b90cfbd7d2f1910061c75269c"

    client = Client(account_sid, auth_token)

    for number,text in zip(numbers,texts):
        message = client.messages.create(
            to="+1" + number,
            from_="+17203998395",
            body=text)



