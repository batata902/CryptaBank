CREATE TABLE IF NOT EXISTS users(
        email TEXT PRIMARY KEY,
        password TEXT,
        wallet TEXT,
        created_at TEXT,
        currency INTEGER,
        tfa INTEGER);
CREATE TABLE IF NOT EXISTS transfer_history(
        source_wallet TEXT,
        destiny_wallet TEXT,
        value TEXT,
        date TEXT
    );