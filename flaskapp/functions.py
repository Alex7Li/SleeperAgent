import numpy as np
import os
from twilio.rest import Client
import random
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse


# checks to the left or right
# names = all names in game
# roles = all roles in game

def espionage(roles):
    texts = []
    n = len(roles)
    right = np.random.randint(0, 2)
    for c in range(len(roles)):
        if right:
            if roles[(c + 1) % n]:
                texts.append("CODE RED: Espionage Detected")
            else:
                texts.append("ALL CLEAR: Espionage NOT Detected")

        else:
            if roles[(c - 1) % n]:
                texts.append("CODE RED: Espionage Detected")
            else:
                texts.append("ALL CLEAR: Espionage NOT Detected")

    send_text(game_data["numbers"],texts)


# set up the game with roles and phone numbers, input number of people
# n = number of players
def setupGameState(n):
    # 0 = good, 1 = bad
    roles = np.zeros(n)
    roles[random.randint(0, n - 1)] = 1
    return roles


# creates names from how many are needed
# num_names = num of players
def nameGenerator(num_names):
    list_names = ['Alpha', 'Bravo', 'Charlie', 'Delta', 'Echo',
                  'Foxtrot', 'Golf', 'Hotel', 'India', 'Juliet',
                  'Kilo', 'Lima', 'Mike', 'November', 'Oscar', 'Papa',
                  'Quebec', 'Romeo', 'Sierra', 'Tango', 'Uniform',
                  'Victor', 'Whiskey', 'X-ray', 'Yankee', 'Zulu']

    return_names = []
    for i in range(num_names):
        name = random.choice(list_names)
        return_names.append("Agent " + name)
        list_names.remove(name)

    return return_names


# # enlists users for new game
# def collect_users_start(numbers):
#     from_number = request.values.get('From', None)
#     if body.lower()=="enlist me":
#         numbers.append(from_number)
#     else:
#         resp = MessagingResponse()
#         resp.message('Permission Denied, text "Enlist Me" to continue')

#     return numbers


# send any text to n number of numbers
def send_text(numbers, texts):
    # Find these values at https://twilio.com/user/account
    # To set up environmental variables, see http://twil.io/secure
    account_sid = "AC3814bc45f99ac5af25d5f45c61cdf33d"
    auth_token = "2de3933b90cfbd7d2f1910061c75269c"

    client = Client(account_sid, auth_token)

    for number, text in zip(numbers, texts):
        message = client.messages.create(
            to="+1" + number,
            from_="+17203998395",
            body=text)


# adds persons choice to press button, checks if everyone has entered
# button_presses = everyone presses so far, global var
# names = all names in game
# name = name of person submitted
# choice = choice of person submitted
# roles = all roles in game
def button(button_presses, numbers, number, choice, roles):
    button_presses[number] = choice

    # checks if everyone has submitted
    done = len(button_presses) == len(numbers)
    if done:
        bad = roles.index(1)
        said_yes = [i for i in button_presses if button_presses[i].lower().replace("'","")=="take"]

        # sends text based on everyone's choices and if bad is in pressed
        for n in button_presses:
            if button_presses[n].lower().replace("'","")=="take" and numbers[bad] in said_yes:
                send_text(n,"There is a traitor amongst you")
                send_text(n,"When you're ready to move on, tell the leader to send next phase")
            elif button_presses[n].lower().replace("'","")=="take" and numbers[bad] not in said_yes:
                send_text(n,"All clear Agent, no one was corrupt")
                send_text(n,"When you're ready to move on, tell the leader to send next phase")
            elif button_presses[n].lower().replace("'","")=="dont take":
                send_text(n,"You've chosen to sit out")
                send_text(n,"When you're ready to move on, tell the leader to send next phase")



# returns how many people should be on the emergency mission
# names = all names in game
def get_emergency_mission_number(names):
    return np.ceil(len(names) / 2)


# determines if bad person is on emergency mission
# roles = all roles in game
# mission_names = all people going on mission
# names = all names in game
def emergency_mission(roles, mission_names, names):
    mission_roles = [r for r, n in zip(roles, names) if n in mission_names]

    if sum(mission_roles) > 0:
        if_bad_on_mission = True
    else:
        if_bad_on_mission = False

    return if_bad_on_mission


# last step, choose someone
# role = role of person who submitted
# choice = their choice
# name = their name
# total_choices = global var of everyone choices
# all names in game
# all roles in game
def excecution(role, choice, name, total_choices, names, roles):
    try:
        total_choices[choice].append(name)
    except:
        for n in names:
            total_choices[n] = []
        total_choices[choice] = [name]

    # if all names are in it calcluates the result
    summer = 0
    for s in total_choices:
        summer += len(total_choices[s])

    result = None
    revote = False
    if summer == len(names):
        done=True
        for n in names:
            bad = roles.index(1)
            # if bad chose themselves they win
            if names[bad] in total_choices[names[bad]]:
                result = False
                break

            # if x num chose bad, good win
            elif len(total_choices[names[bad]]) >= (np.ceil(len(names) / 2) - 1):
                result = True

            else:
                revote = True
    else: done=False

    game_data["total_choices"] = total_choices
    return result, revote, done
