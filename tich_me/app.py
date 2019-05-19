#!/usr/bin/env python3

from appdirs import AppDirs
from pathlib import Path

APP = AppDirs('tich_me')
DB_PATH = Path(APP.user_data_dir) / 'tichu.db'


