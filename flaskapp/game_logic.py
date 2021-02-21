from flaskapp import functions

NO_GAME_MESSAGE = "You are not currently playing a game of Sleeper Agent! " \
                  "Text \"Begin enlisting\" without quotes to start"
IN_MISSION = "Wait for the person who started the mission to text 'Start mission' or exit by texting 'Abort'"


def get_game_id(data, texter_number):
    """
    >>> get_game_id({'id1':{ 'numbers': ['#1', '#2']},'id2': { 'numbers': ["#3", "#4"]}}, '#1')
    'id1'
    >>> get_game_id({'id1':{ 'numbers': ['#1', '#2']},'id2': { 'numbers': ["#3", "#4"]}}, '#4')
    'id2'
    >>> get_game_id({'id1':{ 'numbers': ['#1', '#2']},'id2': { 'numbers': ["#3", "#4"]}}, '#5')
    None
    """
    for game_id in data:
        for phone_number in data[game_id]['numbers']:
            if phone_number == texter_number:
                return game_id
    return None


def determine_response(data, from_number, body):
    """
    Determine how to respond to a given text message,
    or None for no response.
    >>> determine_response({'id1':{ 'numbers': ['#1', '#2']},'id2': { 'numbers': ["#3", "#4"]}}, '#5', 'push')
    'You are not currently playing a game of Sleeper Agent! Text "Begin enlisting" without quotes to start'
    >>> determine_response({'id1':{ 'numbers': ['#1', '#2']}}, '#3', 'enlist me id1')
    'Successfully joined mission id1'
    >>> determine_response({'id1':{ 'numbers': ['#1', '#2']}}, '#1', 'enlist me id1')
    "You are already enlisted in mission id1. Wait for the person who started the mission to text 'Start mission' or exit by texting 'Abort'"
    >>> determine_response({'id1':{ 'numbers': ['#1', '#2']}}, '#1', 'begin enlisting')
    "You are already enlisted in mission id1. Wait for the person who started the mission to text 'Start mission' or exit by texting 'Abort'"
    """
    game_id = get_game_id(data, from_number)
    if game_id is None:
        # Not currently in a game
        if body == "begin enlisting":
            data.id += 1
            game_id = data.id
            add_to_game(game_id, from_number)
            return "Started mission " + game_id + ". Tell others to join by texting 'enlist me " \
                   + game_id + "' to this number without quotes. Start the mission by texting 'Begin enlisting'"
        elif ' '.join(body.split(" ")[:2]) == "enlist me":
            game_id = ''.join(body.split(" ")[2:])
            add_to_game(data[game_id], from_number)
            return "Successfully joined mission " + game_id
        else:
            return NO_GAME_MESSAGE
    # Setting up a game
    if ' '.join(body.split(" ")[:2]) == "enlist me" or body == 'begin enlisting':
        return "You are already enlisted in mission " + game_id + ". " + IN_MISSION
    elif body == 'start mission':
        if len(data[game_id]['numbers']) > 2:
            start_game(game_id)
            return None
        else:
            return "Not enough players, need at least 3 but you only have " + str(len(data[game_id]['numbers']))
    elif body == 'abort':
        remove_from_game(game_id, from_number)
        return "You have left the mission."

    game_data = data[game_id]
    phase = game_data['current_phase']
    if phase == 0:
        if body == 'press' or body == "don't press":
            done = functions.button(game_data['button_presses'], game_data['numbers'],
                                    from_number, body, game_data['roles'])
            if done:
                phase += 1
            else:
                return None
        else:
            return "Please text 'press' or 'don't press' to play"
    if phase == 1 and body == 'next phase':
        functions.espionage(game_data['names'], game_data['roles'])
        phase += 1
        return None


    if phase == 4:
        if game_data["first_time_4"]:
            message = "Now begining the excecution, submit your vote by Agent Name"
            functions.send_text(game_data["numbers"],np.full(len(game_data["numbers"]),message))
            game_data["first_time_4"]= False
        role = roles[game_data["numbers"].index(from_number)]
        choice = body # expects a name
        functions.excecution(role,choice,game_data["total_choices"],game_data["names"],game_data["roles"])


    return None


def add_to_game(game_data, from_number):
    """
    Add a player to the game
    """
    game_data['numbers'] += from_number
    pass


def remove_from_game(game_data, from_phone_number):
    """
    Remove a player from the game
    >>> remove_from_game({'numbers': ["1", "2"]}, 1)
    {'numbers': ["2"]}

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
<<<<<<< HEAD
    game_data['roles'] = functions.setupGameState(len(game_data['numbers']))
    game_data["total_choices"] = {}
    game_data["first_time_0"] = True
    game_data["first_time_1"] = True
    game_data["first_time_2"] = True
    game_data["first_time_3"] = True
    game_data["first_time_4"] = True

=======
    n = len(game_data['numbers'])
    game_data['roles'] += functions.setupGameState(n)
    game_data['names'] += functions.nameGenerator(n)
    functions.send_text(game_data['numbers'],
        ["If you would like to take the lie detector test then HQ will analyze the results and send them " +
         "back to those who took the test. But, the results are aggregated among all people who took the test for " +
         "privacy reasons. Text 'Take' or 'Don't Take'."]*n)
>>>>>>> 3e344c59106ef5299b4afffc8f3d10abb59c3b35

def end_game():
    # session.pop('callers', None)
    pass
