import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DATABASE_URL")

INIT_QUERY = """
CREATE TABLE IF NOT EXISTS apps (
    id SERIAL PRIMARY KEY,
    name VARCHAR(128) NOT NULL UNIQUE,
    api_key TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    app_id INT NOT NULL REFERENCES apps(id),
    type VARCHAR(64) NOT NULL,
    source VARCHAR(128),
    event_data JSONB NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    event_hash VARCHAR(128) NOT NULL,
    auth_signature VARCHAR(256)
);
"""

def init_db():
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    cur.execute(INIT_QUERY)
    conn.commit()
    cur.close()
    conn.close()
    print("DB init done", flush=True)

if __name__ == "__main__":
    init_db() 