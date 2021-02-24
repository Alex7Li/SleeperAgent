from flaskapp.game_logic import determine_response, BEGIN_ENLIST_ST, BEGIN_ENLIST_MID, BEGIN_ENLIST_END, ABORT_MSG
import re


def test_3_player():
    data = {}
    # Players join game
    response = determine_response(data, '#1', 'begin enlisting Jon')
    assert re.match(BEGIN_ENLIST_ST + 'Jon' + BEGIN_ENLIST_MID + '[0-9]+' + BEGIN_ENLIST_END, response)
    response = determine_response(data, '#2', 'enlist 0 Alex')
    assert re.match("Successfully joined mission 0 as Alex", response)
    response = determine_response(data, '#3', 'enlist 0 Lav')
    assert re.match("Successfully joined mission 0 as Lav", response)

    # Lav sucks
    response = determine_response(data, '#3', 'abort')
    assert re.match(ABORT_MSG, response)

    response = determine_response(data, '#4', 'enlist 0 Nick')
    assert re.match("Successfully joined mission 0 as Nick", response)
