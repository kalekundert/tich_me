#!/usr/bin/env python3

import requests
import sqlalchemy
from bs4 import BeautifulSoup
from datetime import datetime
from . import model

BSW_URL = 'http://tichulog.brettspielwelt.de'

def scrape_bsw_month(year, month, progress_ui):
    if year < 2007:
        raise NoDataBefore2007()

    index_url = f'{BSW_URL}/{year}{month:02}/'
    progress_ui.download_index(index_url)

    index_request = requests.get(index_url)
    index_doc = BeautifulSoup(index_request.text, features='lxml')
    game_links = index_doc.find_all('a')

    session = model.init_db()

    for i, a in enumerate(game_links):
        game_url = BSW_URL + a.get('href')
        game_date = datetime.strptime(a.text[:16], '%Y-%m-%d %H:%M')
        progress_ui.download_game(game_url, i, len(game_links))

        if model.is_game_recorded(session, game_url):
            continue

        try:
            scrape_bsw_game(session, game_url, game_date)
            session.commit()
        except Exception as err:
            session.rollback()
            progress_ui.error(game_url, err)

def scrape_bsw_game(session, game_url, game_date=None):
    game_request = requests.get(game_url)
    game_txt = game_request.text

    game = parse_game(game_txt)
    game['url'] = game_url
    game['date'] = game_date

    record_game(session, game)


def parse_game(tch):
    mode = None
    lines = tch.split('\n')

    rounds = []
    players = parse_players(lines)
    player_ids = {v: k for k, v in players.items()}

    for line in lines:
        if not line:
            continue

        tokens = line.split()

        # Work out what kind of line we're looking at.
        if line == '---------------Gr.Tichukarten------------------':
            mode = 'first deal'
            first_deals = {}
            calls = {}
            continue

        if line == '---------------Startkarten------------------':
            mode = 'second deal'
            second_deals = {}
            continue

        if line == 'Schupfen:':
            mode = 'exchange'
            exchanges = {}
            continue

        if line == '---------------Rundenverlauf------------------':
            mode = 'actions'
            wish = None
            plays = {i: set() for i in players}
            finishes = []

        if line.startswith('Ergebnis:'):
            mode = 'round over'

            finishes += list(set(players) - set(finishes))
            round = {
                    'first_deals': first_deals,
                    'second_deals': second_deals,
                    'exchanges': exchanges,
                    'calls': calls,
                    'scores': (int(tokens[1]), int(tokens[3])),
                    'wish': wish,
                    'finishes': finishes
            }
            rounds.append(round)

        # Parse game data
        if mode == 'first deal':
            player = parse_player(tokens[0])
            first_deals[player] = set(tokens[1:])

        if mode == 'second deal':
            if line.startswith('Grosses Tichu:'):
                player = parse_player(tokens[2])
                calls[player] = model.CallTypes.grand_tichu
                continue

            if line.startswith('Tichu:'):
                player = parse_player(tokens[1])
                calls[player] = model.CallTypes.tichu_before
                continue

            player = parse_player(tokens[0])
            second_deals[player] = set(tokens[1:]) - first_deals[player]

        if mode == 'exchange':
            if tokens[0] == 'BOMBE:':
                continue

            giver = parse_player(tokens[0])

            exchanges[giver,player_ids[tokens[2][:-1]]] = tokens[3]
            exchanges[giver,player_ids[tokens[5][:-1]]] = tokens[6]
            exchanges[giver,player_ids[tokens[8][:-1]]] = tokens[9]

        if mode == 'actions':
            if tokens[0] == 'Tichu:':
                player = parse_player(tokens[1])
                calls[player] = model.CallTypes.tichu_after

            elif tokens[0].startswith('Wunsch'):
                wish = (player, tokens[0].split(':')[-1])

            elif tokens[0].startswith('('):
                player = parse_player(tokens[0])
                play = tokens[1]

                if play != 'passt.':
                    plays[player].update(tokens[1:])
                    if len(plays[player]) == 14:
                        finishes.append(player)

    game = {
            'url': None,
            'date': None,
            'players': players,
            'rounds': rounds,
    }
    return game

def parse_players(tch_lines):
    players = {}
    for line in tch_lines[1:5]:
        token = line.split()[0]
        players[int(token[1])] = token[3:]

    return players

def parse_player(token):
    return int(token[1])


def record_game(session, game_dict):
    if model.is_game_recorded(session, game_dict['url']):
        return

    game = model.Game(
            url=game_dict['url'],
            date=game_dict['date'],
    )
    teams, seats = record_players(session, game, game_dict['players'])
    cards = load_cards(session)

    for i, round_dict in enumerate(game_dict['rounds']):
        record_round(session, game, teams, seats, cards, round_dict, i)

def record_players(session, game, players_dict):
    seat_order = {
            0: model.SeatTypes.south,
            1: model.SeatTypes.east,
            2: model.SeatTypes.north,
            3: model.SeatTypes.west,
    }

    # Create the teams for this game.
    teams = [
            model.Team(game=game),
            model.Team(game=game),
    ]
    session.add_all(teams)

    # Create the players.  Fill in the teams and seats.
    team_map = {}
    seat_map = {}

    for i, name in players_dict.items():
        player = model.get_or_create(session, model.Player, name=name)

        team_map[i] = teams[i%2]
        team_map[i].players.add(player)

        seat = model.Seat(game=game, player=player, seat=seat_order[i])
        seat_map[i] = seat
        session.add(seat)

    return team_map, seat_map

def record_round(session, game, teams, seats, cards, round_dict, round_num):
    round = model.Round(game=game, order=round_num)

    # Deals
    record_deal(session, round, seats, cards,
            round_dict['first_deals'], model.DealTypes.first_8)
    record_deal(session, round, seats, cards,
            round_dict['second_deals'], model.DealTypes.second_6)

    # Exchanges
    for (i, j), x in round_dict['exchanges'].items():
        exchange = model.Exchange(
                round=round, 
                giver=seats[i],
                taker=seats[j],
                card=cards[x],
        )
        session.add(exchange)

    # Tichu calls
    for i, call_type in round_dict['calls'].items():
        call = model.Call(
                round=round,
                seat=seats[i],
                call=call_type,
        )
        session.add(call)

    # Wishes:
    if round_dict['wish']:
        i, rank = round_dict['wish']
        wish = model.Wish(
                round=round,
                seat=seats[i],
                rank=rank_map[rank],
        )
        session.add(wish)

    # Finishes:
    for order, i in enumerate(round_dict['finishes']):
        finish = model.Finish(
                round=round,
                seat=seats[i],
                order=order,
        )
        session.add(finish)

    # Scores:
    for i, score in enumerate(round_dict['scores']):
        score = model.Score(
                round=round,
                team=teams[i],
                score=score,
        )

def record_deal(session, round, seats, cards, deal_dict, deal_type):
    for i, deal in deal_dict.items():
        hand = {
                model.Deal(
                    round=round,
                    seat=seats[i],
                    group=deal_type,
                    card=cards[x],
                )
                for x in deal
        }
        session.add_all(hand)

def load_cards(session):
    cards = {}

    for suit in suit_map:
        for rank in rank_map:
            cards[suit+rank] = model.get_or_create(
                    session, model.Card,
                    suit=suit_map[suit],
                    rank=rank_map[rank],
            )

    for special in special_map:
        cards[special] = model.get_or_create(
                session, model.Card,
                special=special_map[special],
        )

    return cards

suit_map = {
        'R': model.SuitTypes.red,
        'G': model.SuitTypes.green,
        'B': model.SuitTypes.blue,
        'S': model.SuitTypes.black,  # "Schwarz" is "black" in German.
}
rank_map = {
        '2':   2,
        '3':   3,
        '4':   4,
        '5':   5,
        '6':   6,
        '7':   7,
        '8':   8,
        '9':   9,
        '10': 10,
        'B':  11,  # "Bauer": Means "farmer", equivalent to jack.
        'D':  12,  # "Dame": Means "lady", equivalent to queen.
        'K':  13,
        'A':  14,
}
special_map = {
        'Ma': model.SpecialTypes.one,   # i.e. "mahjong"
        'Hu': model.SpecialTypes.hound, # "Hund" means "dog" in German.
        'Ph': model.SpecialTypes.phoenix,
        'Dr': model.SpecialTypes.dragon,
}

class NoDataBefore2007(ValueError):

    def __init__(self):
        super().__init__("No game data available before 2007.")
