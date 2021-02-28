# import functions
from flaskapp import functions
import re

NO_GAME_MESSAGE = "You are not currently playing a game of Sleeper Agent! " \
                  "Text \"Begin enlisting your_name_no_spaces\" without quotes to start"
BEGIN_ENLIST_ST = "Began enlisting as "
BEGIN_ENLIST_MID = " ! Tell others to join by texting 'enlist "
BEGIN_ENLIST_END = " their_name_no_spaces' to this number. Start the mission by texting 'Start Mission'"
NO_GAME_ID = "Please enter the game id: text 'enlist game_id name_no_spaces'"
ABORT_MSG = "You have left the mission."
INVALID_COMMAND_PRE_MISSION = "You are in a mission right now. Only the commands " \
                              "Start mission` and `Abort` are allowed."
MISSION_START = "You have started the mission"
LIE_DETECTOR_DESC = "If you would like to take the lie detector test then HQ will analyze the results " \
                    "and send them back to those who took the test. But, the results are aggregated among " \
                    "all people who took the test for privacy reasons. Text 'Take' or 'Don't Take'."
TOO_FEW_PLAYERS = "You cannot start the mission, you need at least 3 players."
SPY_LOSE = "Sorry Comrad, You've been busted"
AGENT_WIN = "Congrats Agents, You caught 'em"
SPY_WIN = "Congrats Comrad, You know too much"
AGENT_LOSE = "Agents Nooo, The sleeper has gotten away"
INVALID_LIE_DETECTOR_INPUT = "Please type in 'take' or 'don't take'"
LIE_DETECTOR_OVER = "The lie detector test has concluded. HQ has developed a new test that will tell you" \
                    "everyone if the person to their right is bad. However, they forgot which way was right, so" \
                    "it might be everyone's left. Text 'next phase' to get the results of espionage"
INVALID_ABORT_TIME = "You can't leave while the game is in progress."
GAME_OVER = "The game has ended. To leave the room, text 'abort'. To play again with the same players," \
            "text `start mission`. To add new players, have them text 'enlist "
ESPIONAGE_END = "Espionage has concluded. HQ has a one final test. Choose half the players rounded up " \
                "to go on a mission, and text their names `name1 name2 name3`. Those players will go on a " \
                "mission and learn if the sleeper is amongst them. The players in the game are: "
MISSION_RE_ENTER = "Please try again, send a list of the names you'd like to go on the mission"
START_EXECUTION = "It's time to seek out the sleeper! Type the name of the Agent that you suspect."
BAD_AGENT_NAME = "There was no agent with that name"


def name_bad(name, name_list):
    if name == 'agent':
        return "You aren't allowed to be agent agent, agent"
    if name in name_list:
        return "That name is taken"
    if re.fullmatch("[a-zA-Z_]+", name) is None:
        return "Names should be only letters and _"
    return False


def response_not_in_game(data, from_number, body):
    # Not currently in a game
    if ' '.join(body.split(" ")[:2]) == "begin enlisting":
        game_id = next_id(data)
        try:
            name = body.split(" ")[2]
            name_is_bad = name_bad(name, [])
            if name_is_bad:
                return name_is_bad
        except IndexError:
            name = functions.nameGenerator([])
        data[game_id] = {'numbers': [from_number], 'names': [name]}
        return BEGIN_ENLIST_ST + name + BEGIN_ENLIST_MID + str(game_id) + BEGIN_ENLIST_END
    elif ' '.join(body.split(" ")[:1]) == "enlist":
        try:
            game_id = body.split(" ")[1]
        except IndexError:
            return NO_GAME_ID
        if game_id not in data:
            return "This game id was not found"
        game_data = data[game_id]
        try:
            name = body.split(" ")[2]
            name_is_bad = name_bad(name, game_data['names'])
            if name_is_bad:
                return name_is_bad
        except IndexError:
            name = functions.nameGenerator(game_data['names'])
        game_data['names'].append(name)
        if game_id in data:
            add_to_game(game_data, from_number)
            return "Successfully joined mission " + game_id + " as " + name
    else:
        return NO_GAME_MESSAGE


def mission_start(game_data):
    if len(game_data['numbers']) >= 3:
        start_game(game_data)
        return MISSION_START
    else:
        return TOO_FEW_PLAYERS


def lie_detector(game_data, body, player_id):
    if body == 'take' or body == "don't take":
        done = functions.button(game_data['button_presses'], game_data['numbers'],
                                player_id, body, game_data['roles'])
        if done:
            game_data['phase'] = 1
            return LIE_DETECTOR_OVER
        else:
            return "Submitted"
    else:
        return INVALID_LIE_DETECTOR_INPUT


def obtain_mission_list(game_data, body):
    # get the mission list
    names = re.split(r'\s+|[ ,;.-]\s*', body)
    try:
        game_data['mission_list'] = sorted(list(set([game_data['names'].index(name) for name in names])))
    except ValueError:
        return "One of the names " + str(names) + " was not the name of an agent"
    n_required = (len(game_data['numbers']) + 1) // 2
    if len(game_data['mission_list']) != n_required:
        return f"Expected {n_required} agent names, got {len(game_data['mission_list'])}"
    mission_names = str(["Agent " + str(game_data['names'][ind]) for ind in game_data['mission_list']])
    game_data['phase'] = 2.5
    return "Is this the mission you'd like: " + mission_names + "? Respond (Y/N)"


def execution_vote(game_data, body, player_id):
    name_regex_results = re.split(r'\s+|[ ,;.-]\s*', body)
    name_ind = None
    for name_possibility in name_regex_results:
        for i in range(len(game_data['names'])):
            if game_data['names'][i] == name_possibility:
                name_ind = i
    if name_ind is None:
        return BAD_AGENT_NAME
    agent_win = functions.excecution(player_id, name_ind, game_data["execution_choices"],
                                     game_data["roles"], game_data['numbers'])
    if agent_win is not None:
        bad_ind = game_data["roles"].index(1)
        if agent_win:
            messages = [AGENT_WIN for _ in range(len(game_data['numbers']))]
            messages[bad_ind] = SPY_LOSE
            functions.send_text(game_data['numbers'], messages)
        else:
            messages = [AGENT_LOSE for _ in range(len(game_data['numbers']))]
            messages[bad_ind] = SPY_WIN
            functions.send_text(game_data['numbers'], messages)
        return "GAME_OVER"
    else:
        return "You voted for Agent " + game_data['names'][name_ind]


def determine_response(data, from_number, body):
    """
    Determine how to respond to a given text message,
    or None for no response.
    """
    game_id = get_game_id(data, from_number)
    if game_id is None:
        return response_not_in_game(data, from_number, body)
    game_data = data[game_id]

    # Setting up a game
    if body == 'start mission':
        return mission_start(game_data)
    elif body == 'abort':
        if 'phase' in game_data:
            return INVALID_ABORT_TIME
        remove_from_game(game_data, from_number)
        if len(game_data['names']) == 0:
            del data[game_id]
        return ABORT_MSG
    elif 'phase' not in game_data:
        return INVALID_COMMAND_PRE_MISSION

    phase = game_data['phase']
    player_id = game_data["numbers"].index(from_number)

    # Lie detector
    if phase == 0:
        return lie_detector(game_data, body, player_id)

    # Espionage
    if phase == 1 and body == 'next phase' and from_number == game_data['numbers'][0]:
        functions.espionage(game_data['numbers'], game_data['roles'])
        game_data['phase'] = 2
        return ESPIONAGE_END + str(game_data['names'])

    # Mission
    if phase == 2 and from_number == game_data['numbers'][0]:
        return obtain_mission_list(game_data, body)

    if phase == 2.5 and from_number == game_data['numbers'][0]:
        if "y" in body:
            game_data['phase'] = 3
            functions.emergency_mission(game_data['roles'], game_data['mission_list'], game_data['numbers'])
            message = START_EXECUTION
            functions.send_text(game_data["numbers"], [message] * len(game_data["numbers"]))
            return None
        else:
            game_data['phase'] = 2
            return MISSION_RE_ENTER

    # Execution
    if phase == 3:
        response_str = execution_vote(game_data, body, player_id)
        if response_str == "GAME_OVER":
            end_game(data, game_id)
        else:
            return response_str
    return None


def get_game_id(data, texter_number):
    """
    >>> get_game_id({'id1':{ 'numbers': ['#1', '#2']},'id2': { 'numbers': ["#3", "#4"]}}, '#1')
    'id1'
    >>> get_game_id({'id1':{ 'numbers': ['#1', '#2']},'id2': { 'numbers': ["#3", "#4"]}}, '#4')
    'id2'
    >>> get_game_id({'id1':{ 'numbers': ['#1', '#2']},'id2': { 'numbers': ["#3", "#4"]}}, '#5')

    """
    for game_id in data:
        for phone_number in data[game_id]['numbers']:
            if phone_number == texter_number:
                return game_id
    return None


def next_id(data):
    id = len(data)
    while str(id) in data:
        id += 1
    return str(id)


def add_to_game(game_data, from_number):
    """
    Add a player to the game
    """
    game_data['numbers'] += [from_number]
    pass


def remove_from_game(game_data, from_phone_number):
    """
    Remove a player from the game
    If roles have already been assigned, don't change anything and return None
    """
    if 'roles' in game_data:
        return None
    ind = game_data['numbers'].index(from_phone_number)
    del game_data['numbers'][ind]
    del game_data['names'][ind]
    return game_data


def start_game(game_data):
    n = len(game_data['numbers'])
    game_data['roles'] = functions.setupGameState(n)
    game_data['phase'] = 0
    game_data['button_presses'] = [None for _ in range(n)]
    game_data["execution_choices"] = [None for _ in range(n)]
    functions.send_text(game_data['numbers'], [LIE_DETECTOR_DESC] * n)


def end_game(data, id):
    del data[id]['roles']
    del data[id]['phase']
    del data[id]['button_presses']
    del data[id]['execution_choices']
    functions.send_text(data[id]['numbers'][0], [GAME_OVER + id + " name_no_spaces'"])
