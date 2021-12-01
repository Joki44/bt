def permission_card(hand, trump, first_card):
    permission_card_first_card = False
    permission_card_trump = False
    permission = []

    for card in hand:
        c = card[1]
        if c == '0':
            c = card[2]
        fc = first_card[1]
        if fc == '0':
            fc = first_card[2]
        
        if c == fc:
            permission.append(card)
            permission_card_first_card = True
            permission_card_trump = True
    
    if permission_card_first_card == False:
        for card in hand:
            c = card[1]
            if c == '0':
                c = card[2]
            t = trump[1]
            if t == '0':
                t = trump[2]
            
            if c == t:
                permission.append(card)
                permission_card_trump = True
    
    if permission_card_trump == False:
        for card in hand:
            permission.append(card)

    return permission


hand = ['9d', '6d', '80s']
trump = '10h'
fc = '6s'

        
print(permission_card(hand, trump, fc))    
