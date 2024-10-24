import sqlite3
import pandas as pd
import os
import sys


def create_database(csv_file, db_file):
    """
    Converts a CSV file to a SQLite database.

    Args:
        csv_file (str): Path to the input CSV file.
        db_file (str): Path to the output SQLite database file.
    """
    # Check if CSV file exists
    if not os.path.exists(csv_file):
        print(f"Error: CSV file '{csv_file}' does not exist.")
        sys.exit(1)

    # Read CSV into DataFrame
    try:
        df = pd.read_csv(csv_file)
        print(f"Successfully read '{csv_file}'.")
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        sys.exit(1)

    # Data Validation: Check for missing 'region' values
    missing_regions = df["region"].isnull().sum()
    if missing_regions > 0:
        print(
            f"Warning: {missing_regions} records have missing 'region' values. Filling with 'UNKNOWN'."
        )
        df["region"] = df["region"].fillna("UNKNOWN")

    # Display first few rows for verification
    print("First few rows of the CSV data:")
    print(df.head())

    # Connect to SQLite database (creates it if not exists)
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        print(f"Connected to SQLite database '{db_file}'.")
    except Exception as e:
        print(f"Error connecting to SQLite database: {e}")
        sys.exit(1)

    # Create 'players' table
    create_table_query = """
    CREATE TABLE IF NOT EXISTS players (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        player TEXT NOT NULL,
        org TEXT,
        rds INTEGER,
        average_combat_score REAL,
        kill_deaths REAL,
        average_damage_per_round REAL,
        kills_per_round REAL,
        assists_per_round REAL,
        first_kills_per_round REAL,
        first_deaths_per_round REAL,
        headshot_percentage REAL,
        clutch_success_percentage REAL,
        clutch_won_played REAL,
        total_kills INTEGER,
        total_deaths INTEGER,
        total_assists INTEGER,
        total_first_kills INTEGER,
        total_first_deaths INTEGER,
        map_id INTEGER,
        agent TEXT,
        region TEXT
    );
    """

    try:
        cursor.execute(create_table_query)
        conn.commit()
        print("Table 'players' is ready.")
    except Exception as e:
        print(f"Error creating table: {e}")
        conn.close()
        sys.exit(1)

    # Insert data into 'players' table using pandas to_sql
    try:
        # Replace NaN with None for SQLite compatibility
        df = df.where(pd.notnull(df), None)

        df.to_sql("players", conn, if_exists="append", index=False)
        print(f"Successfully inserted {len(df)} records into 'players' table.")
    except Exception as e:
        print(f"Error inserting data into table: {e}")
        conn.close()
        sys.exit(1)

    # Close the connection
    conn.close()
    print("Database connection closed.")


if __name__ == "__main__":
    # Define file paths
    csv_file = "players.csv"  # Ensure this is the path to your CSV file
    db_file = "valorant_players.db"  # Desired SQLite DB file

    # Call the function to create the database
    create_database(csv_file, db_file)
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    query = "SELECT * FROM players \
                WHERE region IN ('Japan', 'Russia', 'China', 'ME', 'LATAM') \
                LIMIT 3"
    cursor.execute(query)
    # conn.commit()
    # print("Table 'players' is ready.")
    rows = cursor.fetchall()
    print(rows)
    conn.close()
