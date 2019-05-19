***********************************************
``tich_me`` --- Teach yourself how to win Tichu
***********************************************

`Tichu <https://boardgamegeek.com/boardgame/215/tichu>`_ is a 4-player 
trick-taking game where you play with a partner and wager on whether or not you 
will go out first.  It is not an exceptionally complicated game, but it does 
present a number of interesting strategic decisions for players to make.

In an effort to better understand and inform some of these decisions, `tich_me`
downloads game data from thousands of games played on BrettSpielWelt and 
provides tools to analyze this data.  This allows your decision-making to be 
guided by quantitative information, rather than by intuition.

.. image:: https://img.shields.io/pypi/v/tich_me.svg
   :target: https://pypi.python.org/pypi/tich_me

.. image:: https://img.shields.io/pypi/pyversions/tich_me.svg
   :target: https://pypi.python.org/pypi/tich_me

.. image:: https://img.shields.io/travis/kalekundert/tich_me.svg
   :target: https://travis-ci.org/kalekundert/tich_me

.. image:: https://img.shields.io/coveralls/kalekundert/tich_me.svg
   :target: https://coveralls.io/github/kalekundert/tich_me?branch=master

Installation
============
Install using pip::

   pip install tich_me

You can confirm that the installation succeeded by running this command::

   tich_me -h

Usage
=====
The first step is to download Tichu game logs from BrettSpielWelt and to 
extract the relevant information into a local database::

   tich_me download
   
Note that game logs are downloaded by month.  The default month is the most 
recent one for which no games have been downloaded yet, but it is also possible 
to specify a particular month.

Once this is done, the analysis scripts can be run.  The only analysis 
currently available looks at the probability of being passed particular cards, 
conditional on calling Grand Tichu::

   tich_me analyze passing

This produces the following results:

.. figure:: https://github.com/kalekundert/tich_me/raw/master/analysis/passing_probs.svg?sanitize=true

   The probability of being passed each rank of card in any given round.  The 
   blue bars are if you did not call Tichu or Grand Tichu before the pass, and 
   the orange plus-marks are if you called Grand Tichu.

.. figure:: https://github.com/kalekundert/tich_me/raw/master/analysis/passing_probs_by_giver.svg?sanitize=true

   As above, but separated by who is passing the card to you: your left 
   opponent, your partner, or your right opponent.  Note that the convention of 
   passing odds to the left and evens to the right can clearly be seen.

A broad rule of thumb is that your probability of being passed a 2 is about ½, 
a 3 is about ⅓, a 4 is about ¼, and so on all the way up to 10.  If you call 
Grand Tichu, you are very likely to receive an Ace from your partner and the 
dog from your opponent.  But your are no more likely than usual to receive 2's 
or 3's from your opponents, which surprised me a bit.

Contributing
============
If you are interested in studying a particular aspect of Tichu strategy, 
consider using `tich_me` to do your analysis.  The hard work of downloading, 
parsing, and organizing game data is already done, so you can start doing your 
analysis right away.  And if you do implement a new analysis, please consider 
making a `pull request <https://github.com/kalekundert/vim-coiled-snake/pulls>`_!
`Bug reports <https://github.com/kalekundert/vim-coiled-snake/issues>`_ are also 
very welcome.

