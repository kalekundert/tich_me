#!/usr/bin/env python3

import tich_me, pytest

@pytest.fixture
def db_session(tmp_path):
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    db_path = tmp_path / 'tichu.db'
    engine = create_engine(f'sqlite:///{db_path}')
    tich_me.init_schema(engine)

    Session = sessionmaker(bind=engine)
    return Session()

@pytest.fixture
def now_is_20180704(monkeypatch):
    import datetime

    class patched_datetime(datetime.datetime):
        @classmethod
        def now(cls):
            return datetime.datetime(2018, 7, 4)

    monkeypatch.setattr(datetime, 'datetime', patched_datetime)


def test_most_recent_month_not_downloaded(db_session, now_is_20180704):
    from datetime import datetime

    # If there are no games, this is today's date.
    assert tich_me.most_recent_month_not_downloaded(db_session) == (2018, 7)

    # If there are games, but not this month:
    game = tich_me.Game(date=datetime(2018, 6, 1))
    db_session.add(game)
    db_session.commit()
    assert tich_me.most_recent_month_not_downloaded(db_session) == (2018, 7)

    # If there are games this month:
    game = tich_me.Game(date=datetime(2018, 7, 1))
    db_session.add(game)
    db_session.commit()
    assert tich_me.most_recent_month_not_downloaded(db_session) == (2018, 5)
    
    # Don't crash if there are games without dates:
    game = tich_me.Game()
    db_session.add(game)
    db_session.commit()
    assert tich_me.most_recent_month_not_downloaded(db_session) == (2018, 5)

