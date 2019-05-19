#!/usr/bin/env python3

import tich_me, pytest
from pathlib import Path

DEMO_GAMES = Path(__file__).parent / 'demo_games'

def get_demo_game(name):
    with open(DEMO_GAMES / name) as f:
        return f.read()


def test_parse_player():
    assert tich_me.parse_player('(0)porniroulis:') == 0
    assert tich_me.parse_player('(1)buligan:') == 1
    assert tich_me.parse_player('(2)kostaskostas:') == 2
    assert tich_me.parse_player('(3)AXL13') == 3

def test_parse_round():
    tch = get_demo_game('one_round_no_tichu.tch')
    game = tich_me.parse_game(tch)

    assert game['players'] == {
            0: 'Us_D_Marshal_r_G',
            1: 'lionheart99917',
            2: 'miss.panic',
            3: 'Sayxas',
    }

    assert len(game['rounds']) == 1

    round = game['rounds'][0]

    print(round['first_deals'])
    assert round['first_deals'] == {
            0: {'BK', 'RD', 'BB', 'R9', 'G6', 'G3', 'S2', 'Ma'},
            1: {'GK', 'GB', 'R10', 'B8', 'B7', 'B4', 'R4', 'B3'},
            2: {'BA', 'GD', 'S10', 'S9', 'R6', 'G4', 'B2', 'R2'},
            3: {'Dr', 'RA', 'B10', 'R8', 'G7', 'G5', 'R5', 'B5'},
    }
    assert round['second_deals'] == {
            0: {'Ph', 'GA', 'RK', 'B9', 'R7', 'R3'},
            1: {'SB', 'G10', 'S6', 'S5', 'G2', 'Hu'},
            2: {'SA', 'SK', 'RB', 'G8', 'S8', 'B6'},
            3: {'SD', 'BD', 'G9', 'S7', 'S4', 'S3'},
    }
    assert round['exchanges'] == {
            (0, 1): 'G6',
            (0, 2): 'Ph',
            (0, 3): 'R7',

            (1, 2): 'G2',
            (1, 3): 'GK',
            (1, 0): 'B4',
            
            (2, 3): 'B6',
            (2, 0): 'G4',
            (2, 1): 'R6',

            (3, 0): 'S4',
            (3, 1): 'B10',
            (3, 2): 'S3',
    }
    assert round['calls'] == {}
    assert round['scores'] == (65, 35)
    assert round['wish'] == (0, '2')
    assert round['finishes'] == [2, 1, 3, 0]

def test_parse_grand_tichu():
    tch = get_demo_game('one_round_grand_tichu.tch')
    game = tich_me.parse_game(tch)

    assert len(game['rounds']) == 1
    round = game['rounds'][0]

    assert round['calls'] == {
            1: tich_me.CallTypes.grand_tichu,
    }

def test_parse_tichu_before():
    tch = get_demo_game('one_round_tichu_before.tch')
    game = tich_me.parse_game(tch)

    assert len(game['rounds']) == 1
    round = game['rounds'][0]

    assert round['calls'] == {
            2: tich_me.CallTypes.tichu_before,
    }

def test_parse_tichu_after():
    tch = get_demo_game('one_round_tichu_after.tch')
    game = tich_me.parse_game(tch)

    assert len(game['rounds']) == 1
    round = game['rounds'][0]

    assert round['calls'] == {
            3: tich_me.CallTypes.tichu_after,
    }

def test_incomplete_game():
    tch = get_demo_game('incomplete.tch')
    game = tich_me.parse_game(tch)

    assert len(game['rounds']) == 9

@pytest.mark.skip
def test_player_swap():
    # Can't handle this one yet, and don't care enough to fix it...
    tch = get_demo_game('player_swap.tch')
    game = tich_me.parse_game(tch)
