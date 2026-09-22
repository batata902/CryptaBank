from src.models import User, Transfers, Cards
from src.core import Bank
import sqlite3
from pathlib import Path

bank: Bank = Bank()

from src.commands import *

def seed_database():
    path = Path('src/database')
    path.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect('src/database/database.db')
    conn.executescript(open('schema.sql', 'r').read())

    conn.close()

