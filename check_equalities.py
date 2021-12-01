def check_equalities (players):
    equal = True
    first_player = players[0]
    first_player_bet = first_player['bet']
    for player in players:
        if first_player_bet != player['bet']:
            equal = False
    
    return equal