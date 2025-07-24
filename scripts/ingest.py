import pandas as pd
import sqlite3
import os

INPUT_FILE = "datasets/sp500.csv"
DB_FILE = "datasets/companies.db"

def load_to_sqlite():
    if not os.path.exists(INPUT_FILE):
        print(f"Missing {INPUT_FILE}")
        return

    df = pd.read_csv(INPUT_FILE)

    # Rename columns to match your schema
    df = df.rename(columns={
        "Security": "name",
        "GICS Sector": "industry",
        "Headquarters Location": "country"
    })
    df = df[["name", "industry", "country"]]

    conn = sqlite3.connect(DB_FILE)
    df.to_sql("companies", conn, if_exists="replace", index=False)
    conn.close()
    print(f"Loaded {len(df)} records into {DB_FILE}")

if __name__ == "__main__":
    load_to_sqlite()
