from .game_logic import next_id, remove_from_game
from .functions import nameGenerator, DEFAULT_NAMES
import pytest


def test_next_id_empty():
    data = {}
    assert isinstance(next_id(data), str)


def test_next_id_nonempty():
    data = {'1': {}, '2': {}, '0': {}}
    assert next_id(data) not in {'1', '2', '0'}


def test_next_id_not_full():
    data = {'5': {}, '3': {}, '4': {}}
    assert next_id(data) not in {'1', '3', '4'}


def test_name_gen_empty():
    cur_names = {}
    assert isinstance(nameGenerator(cur_names), str)


def test_name_gen_many_names():
    cur_names = list(DEFAULT_NAMES)[0: -1]
    assert nameGenerator(cur_names) not in cur_names


def test_name_gen_all_names():
    cur_names = list(DEFAULT_NAMES)
    with pytest.raises(AssertionError):
        nameGenerator(cur_names)


def test_remove_from_game():
    game_data = {'numbers': ["1", "2"], 'names': ["Agent India", "Agent Bravo"]}
    assert remove_from_game(game_data, '1') == {'numbers': ["2"], 'names': ["Agent Bravo"]}


def test_remove_from_game_last():
    game_data = {'numbers': ["1"], 'names': ["Agent India"]}
    assert remove_from_game(game_data, '1') == {'numbers': [], 'names': []}


def test_remove_from_game_roles_already_assigned():
    game_data = {'numbers': ["1", "2"], 'names': ["Agent India", "Agent Bravo"], "roles": [0, 1]}
    assert remove_from_game(game_data, '1') is None
    # Its a no op
    assert game_data == {'numbers': ["1", "2"], 'names': ["Agent India", "Agent Bravo"], "roles": [0, 1]}
