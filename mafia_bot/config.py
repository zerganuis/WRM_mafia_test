from pathlib import Path
SQLITE_DB_FILE = Path(__file__).parent.joinpath('db.sqlite3')
print(SQLITE_DB_FILE)