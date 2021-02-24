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
GAME_OVER = "The game has ended. To leave the room, text `abort`. To play again with the same players," \
            "text `start mission`. To add new players, have them text `enlist "
ESPIONAGE_END = "Espionage has concluded. HQ has a one final test. Choose half the players rounded up " \
                "to go on a mission, and text their names `name1 name2 name3`. Those players will go on a " \
                "mission and learn if the sleeper is amongst them. The players in the game are: "
MISSION_PHASE_END = "It's time to seek out the sleeper! Type the name of the Agent that you suspect."
MISSION_RE_ENTER = "Please try again, send a list of the names you'd like to go on the mission"


def determine_response(data, from_number, body):
    """
    Determine how to respond to a given text message,
    or None for no response.
    """
    game_id = get_game_id(data, from_number)
    if game_id is None:
        # Not currently in a game
        if ' '.join(body.split(" ")[:2]) == "begin enlisting":
            game_id = next_id(data)
            try:
                # TODO ensure name is just lowercase + uppercase + _ so there is no conflict
                # in the later stages
                name = body.split(" ")[2]
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
                if name in game_data['names']:
                    return "That name is taken"
            except IndexError:
                name = functions.nameGenerator(game_data['names'])
            game_data['names'].append(name)
            if game_id in data:
                add_to_game(game_data, from_number)
                return "Successfully joined mission " + game_id + " as " + name
        else:
            return NO_GAME_MESSAGE
    game_data = data[game_id]

    # Setting up a game
    if body == 'start mission':
        if len(game_data['numbers']) >= 3:
            start_game(game_data)
            return MISSION_START
        else:
            return TOO_FEW_PLAYERS
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

    # Lie detector/button
    if phase == 0:
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

    # Espionage
    if phase == 1 and body == 'next phase':
        functions.espionage(game_data['numbers'], game_data['roles'])
        game_data['phase'] = 2
        return ESPIONAGE_END + str(game_data['names'])

    # Mission
    if phase == 2 and from_number == game_data['numbers'][0]:
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
        message = "Possible Agents:" + str([name for name in game_data["names"]])
        functions.send_text(game_data["numbers"], [message for _ in range(len(game_data["names"]))])
        game_data['phase'] = 2.5
        return "Is this the mission you'd like: " + mission_names + "? Respond (Y/N)"

    if phase == 2.5 and from_number == game_data['numbers'][0]:
        functions.send_text(game_data["numbers"], [game_data["names"] for i in range(len(game_data["numbers"]))])
        if "y" in body:
            game_data['phase'] = 3
            functions.emergency_mission(game_data['roles'], game_data['mission_list'], game_data['numbers'])
            return MISSION_PHASE_END
        else:
            game_data['phase'] = 2
            return MISSION_RE_ENTER

    if phase == 3:
        message = "Now beginning the execution, submit your vote by Agent Name"
        functions.send_text(game_data["numbers"], [message] * len(game_data["numbers"]))
        game_data['phase'] = 3.5
        return None

    if phase == 3.5:
        role = game_data['roles'][player_id]
        choice = body  # expects a name
        results, revote = functions.excecution(role, choice, game_data["execution_choices"], game_data["names"],
                                               game_data["roles"])
        if results is not None:
            while revote:
                if revote:
                    message = "There is too much disagreement, try voting again"
                    functions.send_text(game_data["numbers"], [message] * len(game_data["numbers"]))
                    results, revote = functions.excecution(role, choice, game_data["execution_choices"],
                                                           game_data["names"],
                                                           game_data["roles"])
                    continue
                bad_ind = game_data["roles"].index(1)
                bad_number = game_data["numbers"][bad_ind]
                good_numbers = list.copy(game_data["numbers"])
                good_numbers.remove(bad_number)

                if results:
                    functions.send_text(bad_number, SPY_LOSE)
                    functions.send_text(good_numbers, [AGENT_WIN for _ in range(len(good_numbers))])
                else:
                    functions.send_text(bad_number, SPY_WIN)
                    functions.send_text(good_numbers, [AGENT_LOSE for _ in range(len(good_numbers))])
                phase += 1
                results, revote = functions.excecution(role, choice, game_data["execution_choices"], game_data["names"],
                                                       game_data["roles"])
        end_game(data, game_id)
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
    >>> remove_from_game({'numbers': ["1", "2"], 'names': ["Agent India", "Agent Bravo"]}, 1)
    {'numbers': ["2"], 'names': ["Agent Bravo"]}

    If roles have already been assigned, don't change anything and return None
    >>> remove_from_game({'numbers': ["1", "2"], 'names': ["Agent India", "Agent Bravo"], 'roles': [0 1]}, 1)
    None
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
    game_data["execution_choices"] = [{} for _ in range(n)]
    functions.send_text(game_data['numbers'], [LIE_DETECTOR_DESC] * n)


def end_game(data, id):
    del data[id]['roles']
    del data[id]['phase']
    del data[id]['button_presses']
    del data[id]['execution_choices']
    functions.send_text(data[id]['numbers'], [GAME_OVER + id + " name_no_spaces`"] * len(data[id]['numbers']))
