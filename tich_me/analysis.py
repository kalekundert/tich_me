#!/usr/bin/env python3

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from . import model

phi = 1.61803398875 

def plot_exchanges(session):
    df = count_exchanges(session)

    plot_exchanges_by_giver(df)
    plot_aggregated_exchanges(df)

    plt.show()

def plot_exchanges_by_giver(df):
    givers = 'left', 'partner', 'right'
    fig, ax = plt.subplots(1, len(givers), figsize=(8, 8/phi))

    for i, giver in enumerate(givers):
        ax[i].set_title(giver)
        plot_exchange_probs(ax[i], df[df.giver == giver])

    fig.tight_layout()

def plot_aggregated_exchanges(df):
    fig, ax = plt.subplots(figsize=(3, 8/phi))

    def agg_prob(x):
        inv_prob = 1 - x
        return 1 - inv_prob.prod()

    df = df.groupby(['call', 'rank'])\
            .agg({'prob': agg_prob, 'count': sum})\
            .reset_index()

    ax.set_title('Probability of being passed')
    plot_exchange_probs(ax, df)

    fig.tight_layout()

def plot_exchange_probs(ax, df, min_counts=20):
    """
    Given data frame must have "call", "rank", and "prob" columns.
    """
    df = df.set_index('call')

    if df.loc['no_call']['count'].sum() > min_counts:
        plot_bars(ax,
                df.loc['no_call']['rank'],
                df.loc['no_call']['prob'],
                linewidth=5,
                color='tab:blue',
        )

    #if df.loc['tichu_before']['count'].sum() > min_counts:
    #    ax.plot(
    #            df.loc['tichu_before']['rank'],
    #            df.loc['tichu_before']['prob'],
    #            marker='_', 
    #            markersize=5,
    #            linestyle='none',
    #            color='tab:orange',
    #    )

    if df.loc['grand_tichu']['count'].sum() > min_counts:
        ax.plot(
                df.loc['grand_tichu']['rank'],
                df.loc['grand_tichu']['prob'],
                marker='+', 
                markersize=5,
                linestyle='none',
                color='tab:orange',
        )

    label_card_axis(ax)

def plot_bars(ax, xs, ys, **kwargs):
    for x, y in zip(xs, ys):
        ax.plot([x, x], [0, y], **kwargs)

def count_exchanges(session):
    from collections import Counter

    counts = Counter()
    queries = query_exchanges_by_call(session)
    givers = {
            (model.SeatTypes.south, model.SeatTypes.west): 'right',
            (model.SeatTypes.east, model.SeatTypes.south): 'right',
            (model.SeatTypes.north, model.SeatTypes.east): 'right',
            (model.SeatTypes.west, model.SeatTypes.north): 'right',

            (model.SeatTypes.south, model.SeatTypes.north): 'partner',
            (model.SeatTypes.east, model.SeatTypes.west): 'partner',
            (model.SeatTypes.north, model.SeatTypes.south): 'partner',
            (model.SeatTypes.west, model.SeatTypes.east): 'partner',

            (model.SeatTypes.south, model.SeatTypes.east): 'left',
            (model.SeatTypes.east, model.SeatTypes.north): 'left',
            (model.SeatTypes.north, model.SeatTypes.west): 'left',
            (model.SeatTypes.west, model.SeatTypes.south): 'left',
    }

    for call in queries:
        for exchange in queries[call].all():
            giver = givers[exchange.giver.seat, exchange.taker.seat]
            rank = get_rank(exchange.card)
            counts[call, giver, rank] += 1

    df = pd.DataFrame([
            dict(
                call=call,
                giver=giver,
                rank=rank,
                count=count,
            )
            for (call, giver, rank), count in counts.items()
    ])

    n = df.groupby(['call', 'giver'])['count'].transform('sum')
    df['prob'] = df['count'] / n

    return df

def query_exchanges_by_call(session):
    from sqlalchemy import and_, or_
    from .model import Exchange, Call, CallTypes

    # Outer join so we can tell which seats *didn't* make a Tichu call.
    q = session.query(Exchange).\
            outerjoin(Call, and_(
                Exchange.round_id == Call.round_id,
                Exchange.taker_id == Call.seat_id,
            ))

    queries = {
            'grand_tichu': q.filter(Call.call == CallTypes.grand_tichu),
            'tichu_before': q.filter(Call.call == CallTypes.tichu_before),
            'no_call': q.filter(or_(
                Call.call == None,
                Call.call == CallTypes.tichu_after,
            )),
    }

    return queries

def label_card_axis(ax):
    named_ranks = {
            11: 'J',
            12: 'Q',
            13: 'K',
            14: 'A',
            **{
                v: special_names[k]
                for k,v in special_rank.items()
            }
    }

    ticks = list(np.arange(NUM_RANKS) + 1)
    tick_labels = [named_ranks.get(x, str(x)) for x in ticks]

    ax.set_xlim(0.5, NUM_RANKS + 0.5)
    ax.set_xticks(ticks)
    ax.set_xticklabels(tick_labels, rotation='vertical')

def get_rank(card):
    if card.special:
        return special_rank[card.special]
    else:
        return card.rank

NUM_RANKS = 17

special_rank = {
        model.SpecialTypes.one: 1,
        model.SpecialTypes.hound: 15,
        model.SpecialTypes.phoenix: 16,
        model.SpecialTypes.dragon: 17,
}
special_names = {
        model.SpecialTypes.one: 'One',
        model.SpecialTypes.hound: 'Dog',
        model.SpecialTypes.phoenix: 'Phoenix',
        model.SpecialTypes.dragon: 'Dragon',
}

