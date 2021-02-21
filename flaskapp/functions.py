import numpy as np
import os
from twilio.rest import Client
import random
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

# checks to the left and right and ra
def espionage(names,roles):
    roles.append(roles[0])
    
    texts = []
    right = np.random.randint(0,2)
    for c in range(len(names)):
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
                
    return names,texts

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


# adds persons choice to press button, checks if everyone has entered
def button(button_presses,names,name,choice):
    button_presses[name]=choice

    # checks if everyone has submitted
    if len(button_presses)==len(names):
        done = True
    else:
        done = False

    return button_presses,done


# returns how many people should be on the emergency mission
def get_emergency_mission_number(names):
    return np.ceil(len(names)/2)

# determines if bad person is on emergency mission
def emergency_mission(roles,mission_names,names,number_in_mission):
    mission_roles = [r for r,n in zip(roles,names) if n in mission_names]

    if sum(mission_roles)>0:
        if_bad_on_mission = True
    else:
        if_bad_on_mission = False

    return if_bad_on_mission


# last step, choose someone
def excecution(role,choice,total_choices,names,roles):
    try:
        total_choices[name].append(choice)
    except:
        total_choices[name] = [choice]

    # if all names are in it calcluates the result
    summer = 0
    for s in total_choices:
        summer+=len(total_choices[s])

    result = None
    if summer==len(names):
        bad = roles.index(1)
        # if bad chose themselves they win
        if names[bad] in total_choices[bad]:
            result = False

        # if x num chose bad, good win
        elif len([names[bad]])>=(np.ceil(len(names)/2)-1):
            result=True

    return total_choices,result
