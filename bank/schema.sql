CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    balance INTEGER NOT NULL,
    key TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS transfers(
    id INTEGER PRIMARY KEY,
    date TEXT NOT NULL,
    source INTEGER NOT NULL REFERENCES users(id),
    destiny INTEGER NOT NULL REFERENCES users(id),
    value INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS cards (
    id INTEGER PRIMARY KEY,
    holder TEXT NOT NULL,
    number TEXT NOT NULL UNIQUE,
    cvv TEXT NOT NULL UNIQUE,
    brand TEXT NOT NULL,
    exp TEXT NOT NULL,
    blocked INTEGER NOT NULL,
    owner INTEGER NOT NULL REFERENCES users(id)
);

INSERT OR IGNORE INTO users(username, password, currency, key) 
VALUES
('guest', 'bfbdb10e7244d30e9225a2bc22658556a50ffc79f032704bcbb96d89469a14b8', 1000, 'guest'), 
('guest2', 'bfbdb10e7244d30e9225a2bc22658556a50ffc79f032704bcbb96d89469a14b8', 10000, 'jeje');

-- guest:senhadaora