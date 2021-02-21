def get_game_id(data, texter_number):
    """
    >>> get_game_id({'id1':{ 'numbers': ['#1', '#2']},'id2': { 'numbers': ["#3", "#4"]}}, '#1')
    'id1'
    >>> get_game_id({'id1':{ 'numbers': ['#1', '#2']},'id2': { 'numbers': ["#3", "#4"]}}, '#4')
    'id2'
    >>> get_game_id({'id1':{ 'numbers': ['#1', '#2']},'id2': { 'numbers': ["#3", "#4"]}}, '#5')
    False
    """
    for game_id in data:
        for phone_number in data[game_id]['numbers']:
            if phone_number == texter_number:
                return game_id
    return False


def start_game(from_number):
    # session['callers'] = [from_number]
    # session['names'] = ['Player 1']
    pass
def end_game():
    # session.pop('callers', None)
    pass
