from flaskapp.game_logic import determine_response, \
    BEGIN_ENLIST_ST, BEGIN_ENLIST_MID, BEGIN_ENLIST_END, \
    IN_MISSION, INVALID_COMMAND_PRE_MISSION, ABORT_MSG, NO_GAME_MESSAGE, \
    MISSION_START, TOO_FEW_PLAYERS
import re


# BEGIN ENLISTING
def test_start_first_mission():
    data = {}
    response = determine_response(data, '1', 'begin enlisting')
    assert re.match(BEGIN_ENLIST_ST + '[A-Za-z]+' + BEGIN_ENLIST_MID + '[0-9]+' + BEGIN_ENLIST_END, response)


def test_start_first_mission_with_name():
    data = {}
    response = determine_response(data, '1', 'begin enlisting Jon')
    assert re.match(BEGIN_ENLIST_ST + 'Jon' + BEGIN_ENLIST_MID + '[0-9]+' + BEGIN_ENLIST_END, response)
    assert len(data) > 0
    assert data == {'0': {'numbers': ['1'], 'names': ['Jon']}}


# JOIN MISSION
def test_join_first_mission():
    data = {'123': {'numbers': ['1'], 'names': ['Kilo']}}
    response = determine_response(data, '2', 'enlist 123')
    assert re.match("Successfully joined mission 123 as " + '[A-Za-z]+', response)
    assert {'numbers': ['1', '2']}.items() <= data['123'].items()


def test_join_mission_with_name():
    data = {'0': {'numbers': ['1'], 'names': ['Kilo']}}
    response = determine_response(data, '3', 'enlist 0 Alex')
    assert re.match("Successfully joined mission 0 as Alex", response)
    assert data == {'0': {'numbers': ['1', '3'], 'names': ['Kilo', 'Alex']}}


def test_join_mission_with_name_taken():
    data = {'10': {'numbers': ['1', '3'], 'names': ['Kilo', 'Milo']}}
    response = determine_response(data, '4', 'enlist 10 Milo')
    assert re.match("That name is taken", response)
    assert data == {'10': {'numbers': ['1', '3'], 'names': ['Kilo', 'Milo']}}


def test_join_mission_doesnt_exist():
    data = {'0': {'numbers': ['1'], 'names': ['Kilo']}}
    response = determine_response(data, '2', 'enlist 33')
    assert re.match("This game id was not found", response)
    assert data == {'0': {'numbers': ['1'], 'names': ['Kilo']}}


def test_join_mission_bad_id():
    data = {'0': {'numbers': ['1'], 'names': ['Kilo']}}
    response = determine_response(data, '2', 'enlist fefej')
    assert re.match("This game id was not found", response)
    assert data == {'0': {'numbers': ['1'], 'names': ['Kilo']}}


def test_join_mission_already_in_mission():
    data = {'0': {'numbers': ['1'], 'names': ['Kilo']}}
    response = determine_response(data, '1', 'enlist 1 Klepto')
    assert re.match(INVALID_COMMAND_PRE_MISSION, response)
    assert data == {'0': {'numbers': ['1'], 'names': ['Kilo']}}


# ABORT

def test_abort_mission_last_member():
    data = {'0': {'numbers': ['1'], 'names': ['Kilo']}}
    response = determine_response(data, '1', 'abort')
    assert re.match(ABORT_MSG, response)
    assert data == {}


def test_abort_mission_not_last_member():
    data = {'0': {'numbers': ['1', '2'], 'names': ['Kilo', 'Philo']}}
    response = determine_response(data, '1', 'abort')
    assert re.match(ABORT_MSG, response)
    assert data == {'0': {'numbers': ['2'], 'names': ['Philo']}}


def test_abort_mission_not_in_mission():
    data = {'0': {'numbers': ['1'], 'names': ['Kilo']}}
    response = determine_response(data, '2', 'abort')
    assert re.match(NO_GAME_MESSAGE, response)
    assert data == {'0': {'numbers': ['1'], 'names': ['Kilo']}}


# START MISSION


def test_start_mission_2_player():
    data = {'0': {'numbers': ['1', '2'], 'names': ['A', 'B']}}
    response = determine_response(data, '1', 'start mission')
    re.match(TOO_FEW_PLAYERS, response)
    assert data == {'0': {'numbers': ['1', '2'], 'names': ['A', 'B']}}


def test_start_mission_3_player():
    data = {'0': {'numbers': ['1', '2', '3'], 'names': ['A', 'B', 'C']}}
    response = determine_response(data, '3', 'start mission')
    re.match(MISSION_START, response)
    assert len(data.items()) == 1
    assert {'numbers': ['1', '2', '3'], 'names': ['A', 'B', 'C'], 'phase': 0,
            'button_presses': {}, 'total_choices': {}
            }.items() <= data['0'].items()
    assert len(data['0']['roles']) == 3
    assert sum(data['0']['roles']) == 1


def test_start_mission_4_player():
    data = {'0': {'numbers': ['1', '2', '3', '4'], 'names': ['A', 'B', 'C', 'D']}}
    response = determine_response(data, '1', 'start mission')
    re.match(MISSION_START, response)
    assert len(data.items()) == 1
    assert {'numbers': ['1', '2', '3', '4'], 'names': ['A', 'B', 'C', 'D'], 'phase': 0,
            'button_presses': {}, 'total_choices': {}
            }.items() <= data['0'].items()
    assert len(data['0']['roles']) == 4
    assert sum(data['0']['roles']) == 1


# BUTTON

def push_button():
    data = {'0': {'numbers': ['1', '2', '3'], 'names': ['A', 'B', 'C'], 'phase': 0,
            'button_presses': {}, 'total_choices': {}, 'roles': [0, 0, 1]
            }}
    pass