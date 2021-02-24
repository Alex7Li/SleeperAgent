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


DEFAULT_NAMES = ('Alpha', 'Bravo', 'Charlie', 'Delta', 'Echo',
                 'Foxtrot', 'Golf', 'Hotel', 'India', 'Juliet',
                 'Kilo', 'Lima', 'Mike', 'November', 'Oscar', 'Papa',
                 'Quebec', 'Romeo', 'Sierra', 'Tango', 'Uniform',
                 'Victor', 'Whiskey', 'Yankee', 'Zulu')


def nameGenerator(names):
    list_names = list(DEFAULT_NAMES)
    while len(list_names) > 0:
        choice = list_names[random.randint(0, len(list_names) - 1)]
        if choice not in names:
            return choice
        list_names.remove(choice)
    raise AssertionError("All names used up")


# send any text to n number of numbers
def send_text(numbers, texts):
    pass
    """
    # Find these values at https://twilio.com/user/account
    # To set up environmental variables, see http://twil.io/secure
    # TODO NICK: We need to put these in environment variables and then access them so that
    # Twilio doesn't reset them
    account_sid = os.environ.get(ACCOUNT_SID)
    auth_token = os.environ.get(AUTH_TOKEN)

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
    """


# adds persons choice to press button, checks if everyone has entered
# button_presses = everyone presses so far, global var
# choice = choice of person submitted
# roles = all roles in game
def button(button_presses, numbers, player_id, choice, roles):
    button_presses[player_id] = choice

    if None in button_presses:
        return False
    bad = roles.index(1)

    said_yes = [i for i in range(len(button_presses)) if button_presses[i] == "take"]

    # sends text based on everyone's choices and if bad is in pressed
    for n in range(len(button_presses)):
        if button_presses[n] == "take" and numbers[bad] in said_yes:
            send_text(n, "There is a traitor amongst those who pushed the button")
            send_text(n, "When you're ready to move on, tell the leader to send next phase")
        elif button_presses[n] == "take" and numbers[bad] not in said_yes:
            send_text(n, "All clear Agent, no one was corrupt")
            send_text(n, "When you're ready to move on, tell the leader to send next phase")
        elif button_presses[n] == "don't take":
            send_text(n, "You've chosen to sit out")
            send_text(n, "When you're ready to move on, tell the leader to send next phase")
    return True


# returns how many people should be on the emergency mission
# names = all names in game
# def get_emergency_mission_number(names):
#     return np.ceil(len(names) / 2)


# determines if bad person is on emergency mission
# roles = all roles in game
# names = all names in game
def emergency_mission(roles, mission_inds, numbers):
    is_bad_on_mission = False

    for i in mission_inds:
        if roles[i] == 1:
            is_bad_on_mission = True

    for i in mission_inds:
        if is_bad_on_mission:
            send_text(numbers[i], "There was a sleeper agent on this mission")
        else:
            send_text(numbers[i], "There was no sleeper agent on this mission")


# last step, choose someone
def excecution(choice, name, execution_choices, names, roles):
    try:
        execution_choices[choice].append(name)
    except:
        for n in names:
            execution_choices[n] = []
        execution_choices[choice] = [name]

    # if all names are in it calculates the result
    summer = 0
    for s in execution_choices:
        summer += len(execution_choices[s])

    result = None
    revote = False
    if summer == len(names):
        result, revote = determine_execution(execution_choices, names, roles)
    return result, revote


def determine_execution(execution_choices, names, roles):
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
    if names[bad] in execution_choices[names[bad]]:
        result = False
    # if x num chose bad, good win
    elif len(execution_choices[names[bad]]) >= (len(names) - 1) // 2:
        result = True
    else:
        revote = True
        for n in names:
            execution_choices[n] = []
    return result, revote
