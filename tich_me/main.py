#!/usr/bin/env python3

def main():
    """\
Improve your Tichu strategy by analyzing trends from thousands of games.

Usage:
    tich_me download [<year> <month>]
    tich_me analyze passing
    tich_me wipe

Database:
    {DB_PATH}
    """
    try:
        import sys
        if sys.argv[1] in globals():
                return globals()[sys.argv[1]]()
        else:
            get_docopt_args(main)

    except KeyboardInterrupt:
        print()

def download():
    """\
Download complete logs for any games that occurred in the specified month, 
and extract the information into a local SQLite database.

Usage:
    tich_me download [<year> <month>]

Database:
    {DB_PATH}
    """
    from . import scrape_bsw_month, model, NoDataBefore2007
    from datetime import datetime

    class Progress:

        def download_index(self, url):
            print("Downloading games from:", url)
            print()
            print("This may take a while.  Hit <Ctrl-C> to abort.")
            print()

        def download_game(self, url, i, n):
            print(f"\r[{i+1}/{n}] {url}", end='')

        def error(self, url, err):
            print()
            print("  Unable to parse above game:", err)

    args = get_docopt_args(download)

    if args['<year>']:
        year = int(args['<year>'])
        month = int(args['<month>'])
    else:
        session = model.init_db()
        year, month = model.most_recent_month_not_downloaded(session)
        print(f"Most recent month not downloaded: {year}-{month:02}")

    try:
        scrape_bsw_month(year, month, Progress())
    except NoDataBefore2007 as err:
        print(err)

def analyze():
    """
    Analyze a particular aspect of Tichu strategy.

    Usage:
        tich_me analyze passing

    Commands:
        passing
            Calculate the probability of being passed each card, conditional on 
            calling Tichu (before the pass) or Grand Tichu.

    Database:
        {DB_PATH}
    """
    from . import analysis, model

    args = get_docopt_args(analyze)
    session = model.init_db()

    if args['passing']:
        analysis.plot_exchanges(session)

def wipe():
    """\
Delete the local database of Tichu games.

Usage:
    tich_me wipe

Database:
    {DB_PATH}
    """
    from . import app

    get_docopt_args(wipe)
    
    # Get confirmation if the database if more than 10MB:
    mb = app.DB_PATH.stat.st_size / 1024**2
    if mb > 10:
        yn = input("The databse is {mb:.0f}MB.  Are you sure you want to wipe it? [Y/n] ")
        if yn == 'n':
            print("Aborted")
            return

    app.DB_PATH.unlink()


def get_docopt_args(f):
    import docopt
    from . import app
    return docopt.docopt(f.__doc__.format(DB_PATH=app.DB_PATH).strip())

