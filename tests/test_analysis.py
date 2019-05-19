#!/usr/bin/env python3

import tich_me, pytest

import sys, os; sys.path.append(os.path.dirname(__file__))
from test_model import db_session
from test_recording import record_demo_game

test_exchanges_by_call_params = {
        'one_round_no_tichu.tch': { 
            'grand_tichu': [],
            'tichu_before': [],
            'no_call': [
                (1, 2, 'G6'),
                (1, 3, '*phoenix*'),
                (1, 4, 'R7'),

                (2, 3, 'G2'),
                (2, 4, 'GK'),
                (2, 1, 'B4'),

                (3, 4, 'B6'),
                (3, 1, 'G4'),
                (3, 2, 'R6'),

                (4, 1, 'K4'),
                (4, 2, 'B10'),
                (4, 3, 'K3'),
            ],
        },
        'one_round_tichu_after.tch': {
            'grand_tichu': [],
            'tichu_before': [],
            'no_call': [
                (1, 2, 'K2'),
                (1, 3, '*dragon*'),
                (1, 4, 'B10'),

                (2, 3, 'K4'),
                (2, 4, 'GK'),
                (2, 1, 'B4'),

                (3, 4, 'B3'),
                (3, 1, 'R6'),
                (3, 2, 'G5'),

                (4, 1, 'R8'),
                (4, 2, 'KQ'),
                (4, 3, 'K7'),
            ],
        },
        'one_round_tichu_before.tch': {
            'grand_tichu': [],
            'tichu_before': [
                (1, 3, '*phoenix*'),
                (2, 3, 'G2'),
                (4, 3, 'K3'),
            ],
            'no_call': [
                (1, 2, 'G6'),
                (1, 4, 'R7'),

                (2, 4, 'GK'),
                (2, 1, 'B4'),

                (3, 4, 'B6'),
                (3, 1, 'G4'),
                (3, 2, 'R6'),

                (4, 1, 'K4'),
                (4, 2, 'B10'),
            ],
        },
        'one_round_grand_tichu.tch': {
            'grand_tichu': [
                (1, 2, 'G8'),
                (3, 2, 'G2'),
                (4, 2, 'RQ'),
            ],
            'tichu_before': [],
            'no_call': [
                (1, 3, '*phoenix*'),
                (1, 4, 'G10'),

                (2, 3, 'R2'),
                (2, 4, 'GA'),
                (2, 1, 'B10'),

                (3, 4, 'B2'),
                (3, 1, 'BA'),

                (4, 1, 'B4'),
                (4, 3, 'R4'),
            ],
        },
        'two_rounds_grand_tichus_diff_seats.tch': {
            'grand_tichu': [
                # First round: "lionheart" calls Grand Tichu
                (1, 2, 'G8'),
                (3, 2, 'G2'),
                (4, 2, 'RQ'),

                # Second round: "Us_D_Marshal_r_G" calls Grand Tichu
                (2, 1, 'K7'),
                (3, 1, 'RA'),
                (4, 1, 'B2'),
            ],
            'tichu_before': [],
            'no_call': [
                (1, 2, [             'R4']),
                (1, 3, ['*phoenix*', '*dragon*']),
                (1, 4, ['G10',       'R7']),

                (2, 3, ['R2',        'R2']),
                (2, 4, ['GA',        'KQ']),
                (2, 1, ['B10',           ]),

                (3, 4, ['B2',        'B8']),
                (3, 1, ['BA',            ]),
                (3, 2, [             'G2']),

                (4, 1, ['B4',            ]),
                (4, 2, [             'RK']),
                (4, 3, ['R4',        'G4']),
            ],
        }
}
@pytest.mark.parametrize('demo', test_exchanges_by_call_params)
def test_exchanges_by_call(db_session, demo):
    record_demo_game(db_session, demo)

    queries = tich_me.query_exchanges_by_call(db_session)
    expected = test_exchanges_by_call_params[demo]

    for k in expected:
        num_exchanges = 0

        # Make sure the expected cards were passed.
        for giver, taker, cards in expected[k]:
            if isinstance(cards, str):
                cards = set([cards])
            num_exchanges += len(cards)

            exchanges = queries[k].filter(
                    tich_me.Exchange.giver_id == giver,
                    tich_me.Exchange.taker_id == taker,
            ).all()

            assert {str(x.card) for x in exchanges} == set(cards)

        # Make sure no unexpected extra cards were passed.
        assert queries[k].count() == num_exchanges

