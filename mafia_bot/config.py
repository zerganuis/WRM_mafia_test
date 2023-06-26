import os
from pathlib import Path

SQLITE_DB_FILE = Path(__file__).parent.joinpath('db.sqlite3')

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    exit("Добавь токен бота в переменную среды TELEGRAM_BOT_TOKEN")