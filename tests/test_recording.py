#!/usr/bin/env python3

import tich_me, pytest

import sys, os; sys.path.append(os.path.dirname(__file__))
from test_model import db_session
from test_parsing import get_demo_game

# These tests are pretty lame.  Hopefully I'll write more as I have trouble 
# with various queries...

def record_demo_game(db_session, name):
    game_txt = get_demo_game(name)
    game_dict = tich_me.parse_game(game_txt)
    tich_me.record_game(db_session, game_dict)
    db_session.commit()


def test_load_cards(db_session):
    cards = tich_me.load_cards(db_session)
    
    assert len(cards) == 56
    assert db_session.query(tich_me.Card).count() == 56

    for card in cards.values():
        if card.special is None:
            assert card.suit is not None and card.rank is not None
        else:
            assert card.suit is None and card.rank is None

def test_query_one_round(db_session):
    record_demo_game(db_session, 'one_round_no_tichu.tch')

    assert db_session.query(tich_me.Player).count() == 4
    assert db_session.query(tich_me.Team).count() == 2
    assert db_session.query(tich_me.Seat).count() == 4
    assert db_session.query(tich_me.Game).count() == 1
    assert db_session.query(tich_me.Round).count() == 1

