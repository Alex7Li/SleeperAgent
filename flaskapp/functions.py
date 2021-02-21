import os
from twilio.rest import Client
import random
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse


# checks to the left or right
# roles = all roles in game


def espionage(roles, numbers):
    """
    >>> espionage([0, 1], ['a', 'b'])

    """
    texts = []
    n = len(roles)
    right = random.randint(0, 1)
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
    send_text(numbers, texts)


# set up the game with roles and phone numbers, input number of people
# n = number of players
def setupGameState(n):
    # 0 = good, 1 = bad
    roles = [0 for i in range(n)]
    roles[random.randint(0, n - 1)] = 1
    return roles


# creates names from how many are needed
# num_names = num of players
def nameGenerator(num_names):
    list_names = ['Alpha', 'Bravo', 'Charlie', 'Delta', 'Echo',
                  'Foxtrot', 'Golf', 'Hotel', 'India', 'Juliet',
                  'Kilo', 'Lima', 'Mike', 'November', 'Oscar', 'Papa',
                  'Quebec', 'Romeo', 'Sierra', 'Tango', 'Uniform',
                  'Victor', 'Whiskey', 'Yankee', 'Zulu']

    return_names = []
    for i in range(num_names):
        name = random.choice(list_names)
        return_names.append("Agent " + name)
        list_names.remove(name)

    return return_names


# send any text to n number of numbers
def send_text(numbers, texts):
    # Find these values at https://twilio.com/user/account
    # To set up environmental variables, see http://twil.io/secure
    account_sid = ""
    auth_token = ""

    client = Client(account_sid, auth_token)
    if isinstance(numbers, str):
        numbers = [numbers]
    if isinstance(texts, str):
        texts = [texts]
    for number, text in zip(numbers, texts):
        client.messages.create(
            to=number,
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

    if len(button_presses) != len(numbers):
        return False
    bad = roles.index(1)

    said_yes = [i for i in button_presses if button_presses[i].lower().replace("'", "") == "take"]

    # sends text based on everyone's choices and if bad is in pressed
    for n in button_presses:
        if button_presses[n].lower().replace("'", "") == "take" and numbers[bad] in said_yes:
            send_text(n, "There is a traitor amongst you")
            send_text(n, "When you're ready to move on, tell the leader to send next phase")
        elif button_presses[n].lower().replace("'", "") == "take" and numbers[bad] not in said_yes:
            send_text(n, "All clear Agent, no one was corrupt")
            send_text(n, "When you're ready to move on, tell the leader to send next phase")
        elif button_presses[n].lower().replace("'", "") == "don't take":
            send_text(n, "You've chosen to sit out")
            send_text(n, "When you're ready to move on, tell the leader to send next phase")
    return True


# returns how many people should be on the emergency mission
# names = all names in game
# def get_emergency_mission_number(names):
#     return np.ceil(len(names) / 2)


# determines if bad person is on emergency mission
# roles = all roles in game
# mission_names = all people going on mission
# names = all names in game
def emergency_mission(roles, mission_names, names):
    # TODO ask alex about a 'set'

    # get the indices of the given names in the set
    agentIDs = []
    for i in range(len(mission_names)):
        for j in range(len(names)):
            shortName = names[j].lower().replace("agent ", "")
        if mission_names[i] == shortName:
            agentIDs.append(j)

    is_bad_on_mission = False

    for i in range(len(agentIDs)):
        if roles[agentIDs[i]] == 1:
            is_bad_on_mission = True

    for i in agentIDs:
        if is_bad_on_mission:
            send_text(game_data['numbers'][i], "There was a sleeper agent on this mission")
        else:
            send_text(game_data['numbers'][i], "There was no sleeper agent on this mission")

    return is_bad_on_mission


# last step, choose someone
# role = role of person who submitted
# choice = their choice
# name = their name
# total_choices = global var of everyone choices
# all names in game
# all roles in game
def excecution(choice, name, total_choices, names, roles):
    try:
        total_choices[choice].append(name)
    except:
        for n in names:
            total_choices[n] = []
        total_choices[choice] = [name]

    # if all names are in it calculates the result
    summer = 0
    for s in total_choices:
        summer += len(total_choices[s])

    result = None
    revote = False
    if summer == len(names):
        result, revote = determine_execution(total_choices, names, roles)
    return result, revote


def determine_execution(total_choices, names, roles):
    """
    >>> determine_execution({'a1':['a2','a3'], 'a2':['a1'], 'a3':[]}, ['a1', 'a2', 'a3'], [1, 0, 0])
    (True, False)
    >>> determine_execution({'a1':['a1','a3'], 'a2':['a2'], 'a3':[]}, ['a1', 'a2', 'a3'], [1, 0, 0])
    (False, False)
    >>> determine_execution({'a1':[], 'a2':['a1', 'a2', 'a3']}, ['a1', 'a2', 'a3'], [1, 0, 0])
    (None, True)
    """
    result = None
    revote = False
    bad = roles.index(1)
    # if bad chose themselves they win
    if names[bad] in total_choices[names[bad]]:
        result = False
    # if x num chose bad, good win
    elif len(total_choices[names[bad]]) >= (len(names) - 1) // 2:
        result = True
    else:
        revote = True
        for n in names:
            total_choices[n] = []
    return result, revote
