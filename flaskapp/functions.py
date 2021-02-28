import os
import sys
from twilio.rest import Client
import random
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

# checks to the left or right
# roles = all roles in game
WAS_SLEEPER = "There was a sleeper agent on this mission"
WAS_NO_SLEEPER = "There was no sleeper agent on this mission"
DISAGREE_MESSAGE = "Not enough people correctly guessed who the sleeper was, try again"
ESP_DETECTED = "CODE RED: A spy is to your left or right"
ESP_CLEAR = "ALL CLEAR: No spies detected"


def espionage(numbers, roles):
    texts = []
    n = len(roles)
    right = random.randint(0, 1)
    for c in range(len(roles)):
        if right:
            if roles[(c + 1) % n]:
                texts.append(ESP_DETECTED)
            else:
                texts.append(ESP_CLEAR)

        else:
            if roles[(c - 1) % n]:
                texts.append(ESP_DETECTED)
            else:
                texts.append(ESP_CLEAR)
    send_text(numbers, texts)


# set up the game with roles and phone numbers, input number of people
# n = number of players
def setupGameState(n):
    # 0 = good, 1 = bad
    roles = [0 for _ in range(n)]
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


TESTING = False


# send any text to n number of numbers
def send_text(numbers, texts):
    if isinstance(numbers, str):
        numbers = [numbers]
    if isinstance(texts, str):
        texts = [texts]
    if TESTING:
        for number, text in sorted(zip(numbers, texts)):
            print(number, text)  # Print the texts to console, tests can check that the right messages are sent.
    else:
        # Find these values at https://twilio.com/user/account
        # To set up environmental variables, see http://twil.io/secure
        # TODO NICK: We need to put these in environment variables and then access them so that
        # Twilio doesn't reset them
        account_sid = os.environ.get("ACCOUNT_SID")
        auth_token = os.environ.get("AUTH_TOKEN")
        client = Client(account_sid, auth_token)

        for number, text in zip(numbers, texts):
            client.messages.create(
                to=number,
                from_="+17203998395",
                body=text)


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
        recv = numbers[n]
        if button_presses[n] == "take" and numbers[bad] in said_yes:
            send_text(recv, "There is a traitor amongst those who pushed the button")
            send_text(recv, "When you're ready to move on, tell the leader to send next phase")
        elif button_presses[n] == "take" and numbers[bad] not in said_yes:
            send_text(recv, "All clear Agent, no one was corrupt")
            send_text(recv, "When you're ready to move on, tell the leader to send next phase")
        elif button_presses[n] == "don't take":
            send_text(recv, "You've chosen to sit out")
            send_text(recv, "When you're ready to move on, tell the leader to send next phase")
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
            send_text(numbers[i], WAS_SLEEPER)
        else:
            send_text(numbers[i], WAS_NO_SLEEPER)


# last step, choose someone

def excecution(voter_id, votee_id, execution_choices, roles, numbers):
    execution_choices[voter_id] = votee_id

    # if all names are in it calculates the result
    agent_win = None
    if None not in execution_choices:
        agent_win = determine_execution(execution_choices, roles)
        if agent_win is None:
            message = DISAGREE_MESSAGE
            send_text(numbers, [message for _ in range(len(numbers))])
            for i in range(len(roles)):
                execution_choices[i] = None
    return agent_win


def determine_execution(execution_choices, roles):
    """
    >>> determine_execution([1, 0, 0], [1, 0, 0])
    True
    >>> determine_execution([0,0,0], [1, 0, 0])
    False
    >>> determine_execution([1,1,1], [1, 0, 0])
    None
    """
    agent_win = None
    bad = roles.index(1)
    # If bad chose themselves they win
    if execution_choices[bad] == bad:
        agent_win = False
    # If x num chose bad, good win
    elif sum(vote == bad for vote in execution_choices) >= (len(execution_choices) - 1) // 2:
        agent_win = True
    return agent_win
