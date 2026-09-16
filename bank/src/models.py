from __future__ import annotations

from src.utils import gerar_cartao

import random
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from hashlib import sha256
from datetime import datetime
import secrets

@contextmanager
def db():
    conn = sqlite3.connect('src/database/database.db')
    conn.row_factory = sqlite3.Row

    cur = conn.cursor()

    try:
        yield conn, cur
    finally:
        conn.close()

@dataclass
class User:
    id: int
    username: str
    password: str
    _balance: int
    key: str

    @property
    def balance(self) -> int:
        with db() as (_, cur):
            self._balance = cur.execute('SELECT balance FROM users WHERE id = ?', (self.id,)).fetchone()['balance']
        return self._balance

    @balance.setter
    def balance(self, value: int):
        if not value:
            raise ValueError('balance não pode ser vazia')

        self._balance = value

        
    @classmethod
    def load_user(cls, user_id: int) -> User | None:
        with db() as (_, cur):
            user = cur.execute('SELECT * FROM users WHERE id=?;', (user_id,)).fetchone()
        if not user:
            return None

        return cls(
            id = user['id'],
            username = user['username'],
            password = user['password'],
            _balance = user['balance'],
            key = user['key']
            )   

    @classmethod
    def log_in(cls, username: str, password: str) -> User | None:
        with db() as (_, cur):
            user = cur.execute('SELECT * FROM users WHERE username=?;', (username,)).fetchone()

        if not user:
            return None
        
        if user['password'] == sha256(password.encode('utf-8')).hexdigest():
            return cls.load_user(user['id'])

    @staticmethod
    def create_user(username: str, password: str) -> bool:
        password: str = sha256(password.encode('utf-8')).hexdigest()

        key = secrets.token_urlsafe(6)
        with db() as (conn, cur):
            while True:
                k = cur.execute('SELECT id FROM users WHERE key=?;', (key,)).fetchone()
                if k:
                    key = secrets.token_urlsafe(6)
                    continue
                break

            try:
                cur.execute('INSERT INTO users(username, password, balance, key) VALUES(?, ?, ?, ?);', (username, password, 0, key))
            except sqlite3.IntegrityError:
                return False

            conn.commit()

        return True

    def update_key(self, key) -> bool:
        with db() as (conn, cur):
            try:
                cur.execute('UPDATE users SET key=? WHERE id=?', (key, self.id))
                conn.commit()
            except sqlite3.IntegrityError:
                return False

        self.key = key
        return True


@dataclass
class Transfers:
    id: int
    source: str
    destiny: str
    value: int

    @classmethod
    def get_transfer(cls, t_id: str) -> Transfers | None:
        with db() as (_, cur):
            t = cur.execute('SELECT t.id, t.value u.username AS source, u2.username AS destiny FROM transfers t JOIN users u ON u.id=t.source JOIN users u2 ON u2.id=t.destiny WHERE t.id=?', (t_id,)).fetchone()
        if t:
            return cls(
                id = t['id'],
                source = t['source'],
                destiny = t['destiny'],
                value = t['value']
            )
        return None

    @classmethod
    def list_user_transfs(cls, user_id: str) -> list[Transfers]:
        with db() as (_, cur):
            query = cur.execute('SELECT * FROM transfers WHERE source=? OR destiny=?', (user_id, user_id)).fetchall()
        transfs = [dict(row) for row in query]

        return transfs


@dataclass
class Cards:
    id: int
    holder: str
    number: str
    cvv: str
    brand: str
    exp: str
    blocked: bool
    owner_id: int

    @classmethod
    def get_card(cls, card_id: int) -> Cards | None:
        with db() as (_, cur):
            card = cur.execute('SELECT * FROM cards WHERE id=?;', (card_id,)).fetchone()

            if not card:
                return None
        return cls(
            id=card['id'],
            holder=card['holder'],
            number=card['number'],
            cvv=card['cvv'],
            brand=card['brand'],
            exp=card['exp'],
            blocked=card['blocked'],
            owner_id=card['owner']
        )

    @staticmethod
    def list_user_cards(user: User) -> list[dict] | None:
        with db() as (_, cur):
            cards = cur.execute('SELECT * FROM cards WHERE owner=?;', (user.id,)).fetchall()
            if not cards:
                return None

        return [dict(card) for card in cards]


    @staticmethod
    def create_card(user: User, name: str) -> bool:
        card_num: str = gerar_cartao("5", 16)
        with db() as (conn, cur):
            cur.execute(
                'INSERT OR IGNORE INTO cards(holder, number, cvv, brand, exp, blocked, owner) VALUES(?, ?, ?, ?, ?, ?, ?)', 
                (name, card_num, "".join([str(random.randint(0, 9)) for _ in range(3)]), 'CryptaB', '04/30', 0, user.id)
            )

            try:
                conn.commit()
            except sqlite3.IntegrityError:
                return False
        return True

    @staticmethod
    def delete_card(card_id: str) -> None:
        with db() as (conn, cur):
            cur.execute('DELETE FROM cards WHERE id=?;', (card_id,))
            conn.commit()
       

    @staticmethod
    def update_card(card_id: str, block: str) -> bool:
        try:
            block = int(block)
            if block != 0 and block != 1:
                return False
            
        except ValueError:
            return False
        
        with db() as (conn, cur):
            card = cur.execute('SELECT * FROM cards WHERE id=?;', (card_id,)).fetchone()
            if not card:
                return False

            cur.execute('UPDATE cards SET blocked=? WHERE id=?', (block, card_id))
            conn.commit()

        return True

    @staticmethod
    def get_cards_infos(card_number: str) -> dict | None:
        with db() as (_, cur):
            card = cur.execute('SELECT * FROM cards WHERE number=?;', (card_number,)).fetchone()
        if not card:
            return None

        return dict(card)

    @staticmethod
    def transfer(user_id: int, destiny: str, value: int, card_number: str, cvv: str) -> bool:

            current_user: User = User.load_user(user_id)
            current_card: dict = Cards.get_cards_infos(card_number)
            if not current_card:
                return False

            if current_card['cvv'] != cvv:
                return False
            
            if value > current_user.balance:
                return False
    
            current_date: str = datetime.now().strftime("%d/%m/&Y:%H-%M")
            
            with db() as (conn, cur):
                try:
                    cur.execute('BEGIN IMMEDIATE') # Impede race conditions aqui
    
                    dest = cur.execute('SELECT * FROM users WHERE key=?;', (destiny,)).fetchone()
    
                    if dest:
                        cur.execute('UPDATE users SET balance=balance - ? WHERE id=?', (value, current_user.id))
                        if cur.rowcount == 0:
                            conn.rollback()
                            return False
    
                        cur.execute('UPDATE users SET balance=balance + ? WHERE id=?', (value, dest['id']))
    
                        cur.execute('INSERT INTO transfers(source, destiny, value, date) VALUES(?, ?, ?, ?)', (current_user.id, dest['id'], value, current_date))
    
                        conn.commit()
                        current_user._balance -= int(value)
    
                        return True
                    
                except (sqlite3.Error, ValueError):
                    conn.rollback()
                    return False
    
            return False