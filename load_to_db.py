import pandas as pd
from sqlalchemy import create_engine
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from config import POSTGRES

# Build connection string for the initial connection to 'postgres' database
default_conn_str = (
    f"dbname=postgres user={POSTGRES['user']} "
    f"password={POSTGRES['password']} host={POSTGRES['host']} port={POSTGRES['port']}"
)

try:
    print("Connecting to 'postgres' database to set up soccer_db...")
    conn = psycopg2.connect(default_conn_str)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    # Check if the target database already exists
    cur.execute(
        "SELECT 1 FROM pg_database WHERE datname = %s;", (POSTGRES['database'],)
    )
    exists = cur.fetchone()

    if not exists:
        cur.execute(f"CREATE DATABASE {POSTGRES['database']}")
        print(f"Database '{POSTGRES['database']}' created.")
    else:
        print(f"Database '{POSTGRES['database']}' already exists.")

    cur.close()
    conn.close()
except Exception as e:
    print(f"Failed to create database: {e}")
    exit(1)

# Connect to the target database
conn_str = (
    f"postgresql://{POSTGRES['user']}:{POSTGRES['password']}"
    f"@{POSTGRES['host']}:{POSTGRES['port']}/{POSTGRES['database']}"
)

engine = create_engine(conn_str)
print(f"Connected to database '{POSTGRES['database']}'.")

# Load cleaned men's data
print("Loading men_cleaned.csv...")
df_men = pd.read_csv("data/men/men_cleaned.csv")
df_men.to_sql("matches_men", engine, if_exists="replace", index=False)
print(f"Inserted {len(df_men)} rows into matches_men table.")

# Load cleaned women's data
print("Loading women_cleaned.csv...")
df_women = pd.read_csv("data/women/women_cleaned.csv")
df_women.to_sql("matches_women", engine, if_exists="replace", index=False)
print(f"Inserted {len(df_women)} rows into matches_women table.")

print("Data load complete.")
