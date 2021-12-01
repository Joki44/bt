from os import closerange
from aiogram.utils.mixins import T


def card_seniority(trump, card_suit, cards):
    t = trump[1]
    if t == '0':
        t = trump[2]

    cs = card_suit[1]
    if cs == '0':
        cs = card_suit[2]

    seniority = {}

    if t == 'h' and cs == 'd':
        seniority = {
            '6s':  1, '7s':  2, '8s':  3, '9s':  4, '10s':  5, 'Js':  6, 'Qs':  7, 'Ks':  8, 'As':  9,
            '6d': 10, '7d': 11, '8d': 12, '9d': 13, '10d': 14, 'Jd': 15, 'Qd': 16, 'Kd': 17, 'Ad': 18,
            '6h': 19, '7h': 20, '8h': 21, '9h': 22, '10h': 23, 'Jh': 24, 'Qh': 25, 'Kh': 26, 'Ah': 27
        }

    if t == 'h' and cs == 's':
        seniority = {
            '6d':  1, '7d':  2, '8d':  3, '9d':  4, '10d':  5, 'Jd':  6, 'Qd':  7, 'Kd':  8, 'Ad':  9,
            '6s': 10, '7s': 11, '8s': 12, '9s': 13, '10s': 14, 'Js': 15, 'Qs': 16, 'Ks': 17, 'As': 18,
            '6h': 19, '7h': 20, '8h': 21, '9h': 22, '10h': 23, 'Jh': 24, 'Qh': 25, 'Kh': 26, 'Ah': 27
        }

    if t == 'h' and cs == 'h':
        seniority = {
            '6d':  0, '7d':  0, '8d':  0, '9d':  0, '10d':  0, 'Jd':  0, 'Qd':  0, 'Kd':  0, 'Ad':  0,
            '6s':  0, '7s':  0, '8s':  0, '9s':  0, '10s':  0, 'Js':  0, 'Qs':  0, 'Ks':  0, 'As':  0,
            '6h':  1, '7h':  2, '8h':  3, '9h':  4, '10h':  5, 'Jh':  6, 'Qh':  7, 'Kh':  8, 'Ah':  9
        }

    if t == 'd' and cs == 'h':
        seniority = {
            '6s':  1, '7s':  2, '8s':  3, '9s':  4, '10s':  5, 'Js':  6, 'Qs':  7, 'Ks':  8, 'As':  9,
            '6h': 10, '7h': 11, '8h': 12, '9h': 13, '10h': 14, 'Jh': 15, 'Qh': 16, 'Kh': 17, 'Ah': 18,
            '6d': 19, '7d': 20, '8d': 21, '9d': 22, '10d': 23, 'Jd': 24, 'Qd': 25, 'Kd': 26, 'Ad': 27
        }

    if t == 'd' and cs == 's':
        seniority = {
            '6h':  1, '7h':  2, '8h':  3, '9h':  4, '10h':  5, 'Jh':  6, 'Qh':  7, 'Kh':  8, 'Ah':  9,
            '6s': 10, '7s': 11, '8s': 12, '9s': 13, '10s': 14, 'Js': 15, 'Qs': 16, 'Ks': 17, 'As': 18,
            '6d': 19, '7d': 20, '8d': 21, '9d': 22, '10d': 23, 'Jd': 24, 'Qd': 25, 'Kd': 26, 'Ad': 27
        }


    if t == 'd' and cs == 'd':
        seniority = {
            '6h': 0, '7h': 0, '8h': 0, '9h': 0, '10h': 0, 'Jh': 0, 'Qh': 0, 'Kh': 0, 'Ah': 0,
            '6s': 0, '7s': 0, '8s': 0, '9s': 0, '10s': 0, 'Js': 0, 'Qs': 0, 'Ks': 0, 'As': 0,
            '6d': 1, '7d': 2, '8d': 3, '9d': 4, '10d': 5, 'Jd': 6, 'Qd': 7, 'Kd': 8, 'Ad': 9
        }


    if t == 's' and cs == 'd':
        seniority = {
            '6h':  1, '7h': 2,  '8h':  3, '9h':  4, '10h':  5, 'Jh':  6, 'Qh':  7, 'Kh':  8, 'Ah':  9,
            '6d': 10, '7d': 11, '8d': 12, '9d': 13, '10d': 14, 'Jd': 15, 'Qd': 16, 'Kd': 17, 'Ad': 18,
            '6s': 19, '7s': 20, '8s': 21, '9s': 22, '10s': 23, 'Js': 24, 'Qs': 25, 'Ks': 26, 'As': 27
        }


    if t == 's' and cs == 'h':
        seniority = {
            '6d':  1, '7d':  2, '8d':  3, '9d':  4, '10d':  5, 'Jd':  6, 'Qd':  7, 'Kd':  8, 'Ad':  9,
            '6h': 10, '7h': 11, '8h': 12, '9h': 13, '10h': 14, 'Jh': 15, 'Qh': 16, 'Kh': 17, 'Ah': 18,
            '6s': 19, '7s': 20, '8s': 21, '9s': 22, '10s': 23, 'Js': 24, 'Qs': 25, 'Ks': 26, 'As': 27
        }


    if t == 's' and cs == 's':
        seniority = {
            '6d':  0, '7d':  0, '8d':  0, '9d':  0, '10d':  0, 'Jd':  0, 'Qd':  0, 'Kd':  0, 'Ad':  0,
            '6h': 0, '7h': 0, '8h': 0, '9h': 0, '10h': 0, 'Jh': 0, 'Qh': 0, 'Kh': 0, 'Ah': 0,
            '6s': 19, '7s': 20, '8s': 21, '9s': 22, '10s': 23, 'Js': 24, 'Qs': 25, 'Ks': 26, 'As': 27
        }

    print(seniority[cards[0]])
    vin = seniority[cards[0]]
    vincard = cards[0]

    for card in cards:
        if seniority[card] > vin:
            vin = seniority[card]
            vincard = card



    return vincard

# print(card_seniority('6s', '6d', ['6s', '7h', '10s']))