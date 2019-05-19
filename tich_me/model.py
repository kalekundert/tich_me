#!/usr/bin/env python3

from enum import Enum

class SuitTypes(Enum):
    red = 1
    green = 2
    blue = 3
    black = 4

class SpecialTypes(Enum):
    one = 1
    hound = 2
    phoenix = 3
    dragon = 4

class DealTypes(Enum):
    first_8 = 1
    second_6 = 2

class CallTypes(Enum):
    grand_tichu = 1
    tichu_before = 2  # i.e. before the exchange.
    tichu_after = 3

class SeatTypes(Enum):
    south = 1
    east = 2
    north = 3
    west = 4

from sqlalchemy import Table, Column, ForeignKey, UniqueConstraint
from sqlalchemy import Integer, String, Enum, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import relationship

from functools import partial

Base = declarative_base()
Column = partial(Column, nullable=False)
relationship = partial(relationship, collection_class=set)

# For reasons I don't fully understand, association tables for many-to-many 
# relationships can't be defined using the ORM (i.e. via a class).
teammate = Table('teammate', Base.metadata,
    Column('player_id', Integer, ForeignKey('player.id')),
    Column('team_id', Integer, ForeignKey('team.id')),
)

class Player(Base):
    __tablename__ = 'player'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    teams = relationship('Team', back_populates='players', secondary=teammate)
    seats = relationship('Seat', back_populates='player')

class Game(Base):
    __tablename__ = 'game'

    id = Column(Integer, primary_key=True)
    url = Column(String, nullable=True)
    date = Column(DateTime, nullable=True)

    teams = relationship('Team', back_populates='game')
    seats = relationship('Seat', back_populates='game')
    rounds = relationship('Round', back_populates='game')

class Team(Base):
    __tablename__ = 'team'

    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('game.id'))

    game = relationship('Game', back_populates='teams')
    players = relationship('Player', back_populates='teams', secondary=teammate)
    scores = relationship('Score', back_populates='team')

class Seat(Base):
    __tablename__ = 'seat'

    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('game.id'))
    player_id = Column(Integer, ForeignKey('player.id'))
    seat = Column(Enum(SeatTypes))

    game = relationship('Game', back_populates='seats')
    player = relationship('Player', back_populates='seats')
    deal = relationship('Deal', back_populates='seat')
    finishes = relationship('Finish', back_populates='seat')

    UniqueConstraint('player_id', 'team_id')

class Round(Base):
    __tablename__ = 'round'

    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('game.id'))
    order = Column(Integer)

    game = relationship('Game', back_populates='rounds')
    deals = relationship('Deal', back_populates='round')
    exchanges = relationship('Exchange', back_populates='round')
    calls = relationship('Call', back_populates='round')
    wishes = relationship('Wish', back_populates='round')
    finishes = relationship('Finish', back_populates='round')
    scores = relationship('Score', back_populates='round')

    UniqueConstraint('game', 'order')

class Deal(Base):
    __tablename__ = 'deal'

    id = Column(Integer, primary_key=True)
    round_id = Column(Integer, ForeignKey('round.id'))
    seat_id = Column(Integer, ForeignKey('seat.id'))
    card_id = Column(Integer, ForeignKey('card.id'))
    group = Column(Enum(DealTypes))

    round = relationship('Round', back_populates='deals')
    seat = relationship('Seat', back_populates='deal')
    card = relationship('Card')

    UniqueConstraint('round_id', 'seat_id', 'card_id')

class Exchange(Base):
    __tablename__ = 'exchange'

    id = Column(Integer, primary_key=True)
    round_id = Column(Integer, ForeignKey('round.id'))
    giver_id = Column(Integer, ForeignKey('seat.id'))
    taker_id = Column(Integer, ForeignKey('seat.id'))
    card_id = Column(Integer, ForeignKey('card.id'))

    round = relationship('Round', back_populates='exchanges')
    giver = relationship('Seat', foreign_keys=giver_id)
    taker = relationship('Seat', foreign_keys=taker_id)
    card = relationship('Card')

    UniqueConstraint('round', 'giver', 'taker')

    def __repr__(self):
        return f'<Exchange round={self.round_id} giver={self.giver_id} taker={self.taker_id}, card={self.card}>'

class Call(Base):
    __tablename__ = 'call'

    id = Column(Integer, primary_key=True)
    round_id = Column(Integer, ForeignKey('round.id'))
    seat_id = Column(Integer, ForeignKey('seat.id'))
    call = Column(Enum(CallTypes))

    round = relationship('Round', back_populates='calls')
    seat = relationship('Seat')

    UniqueConstraint('round', 'seat', 'call')

class Wish(Base):
    __tablename__ = 'wish'

    id = Column(Integer, primary_key=True)
    round_id = Column(Integer, ForeignKey('round.id'))
    seat_id = Column(Integer, ForeignKey('seat.id'))
    rank = Column(Integer, nullable=True)

    round = relationship('Round', back_populates='wishes')
    seat = relationship('Seat')

    UniqueConstraint('round', 'seat')

class Finish(Base):
    __tablename__ = 'finish'

    id = Column(Integer, primary_key=True)
    round_id = Column(Integer, ForeignKey('round.id'))
    seat_id = Column(Integer, ForeignKey('seat.id'))
    order = Column(Integer)

    round = relationship('Round', back_populates='finishes')
    seat = relationship('Seat', back_populates='finishes')

    UniqueConstraint('round', 'seat')

class Score(Base):
    __tablename__ = 'score'

    id = Column(Integer, primary_key=True)
    round_id = Column(Integer, ForeignKey('round.id'))
    team_id = Column(Integer, ForeignKey('team.id'))
    score = Column(Integer)

    # num_5s = Column(Integer)
    # num_10s = Column(Integer)
    # num_kings = Column(Integer)
    # have_dragon = Column(Boolean)
    # have_phoenix = Column(Boolean)
    # tichu = Column(Enum(TichuOutcomeTypes))

    round = relationship('Round', back_populates='scores')
    team = relationship('Team', back_populates='scores')

    UniqueConstraint('round', 'team')

class Card(Base):
    __tablename__ = 'card'

    id = Column(Integer, primary_key=True)
    rank = Column(Integer, nullable=True)
    suit = Column(Enum(SuitTypes), nullable=True)
    special = Column(Enum(SpecialTypes), nullable=True)

    def __repr__(self):
        special_abbr = {
                SpecialTypes.dragon: '*dragon*',
                SpecialTypes.phoenix: '*phoenix*',
                SpecialTypes.hound: '*dog*',
                SpecialTypes.one: '*1*',
        }
        suit_abbr = {
                SuitTypes.red: 'R',
                SuitTypes.blue: 'B',
                SuitTypes.green: 'G',
                SuitTypes.black: 'K',
        }
        rank_abbr = {
                11: 'J',
                12: 'Q',
                13: 'K',
                14: 'A',
        }
        if self.special:
            return special_abbr[self.special]
        else:
            return f'{suit_abbr[self.suit]}{rank_abbr.get(self.rank, self.rank)}'

def init_db():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from .app import DB_PATH

    DB_PATH.parent.mkdir(exist_ok=True)

    engine = create_engine(f'sqlite:///{DB_PATH}')
    init_schema(engine)

    Session = sessionmaker(bind=engine)
    return Session()

def init_schema(engine):
    Base.metadata.create_all(engine)

def is_game_recorded(session, url):
    if url is None: return False
    return session.query(Game).filter_by(url=url).count()

def most_recent_month_not_downloaded(session):
    from datetime import datetime

    game_dates = {
            (x.date.year, x.date.month)
            for x in session.query(Game).all()
            if x.date is not None
    }

    now = datetime.now()
    next_year = now.year
    next_month = now.month

    while True:
        next_date = next_year, next_month

        if next_date not in game_dates:
            return next_date

        if next_month == 1:
            next_year -= 1
            next_month = 12
        else:
            next_month -= 1

def get_or_create(session, model, **kwargs):
    try: 
        row = session.query(model).filter_by(**kwargs).one()
        return row
    except NoResultFound:
        row = model(**kwargs)
        session.add(row)
        return row



