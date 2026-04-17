import os
import sqlite3
import pandas as pd

# Base directory (project root)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Paths
RAW_DIR = os.path.join(BASE_DIR, "data", "raw", "csv")
DB_DIR = os.path.join(BASE_DIR, "db")
DB_PATH = os.path.join(DB_DIR, "healthcare_ml.db")

# Create db folder if not exists
os.makedirs(DB_DIR, exist_ok=True)

# Connect to SQLite DB
conn = sqlite3.connect(DB_PATH)
print("RAW_DIR:", RAW_DIR)
print("Files inside RAW_DIR:", os.listdir(RAW_DIR))

# Loop through raw files
for file_name in os.listdir(RAW_DIR):
    file_path = os.path.join(RAW_DIR, file_name)

    # Skip if it's a folder
    if not os.path.isfile(file_path):
        continue

    try:
        # Read CSV
        df = pd.read_csv(file_path)

        # Table name from file name
        table_name = os.path.splitext(file_name)[0].lower()

        # Load into SQLite
        df.to_sql(table_name, conn, if_exists="replace", index=False)

        print(f"Loaded {file_name} → table '{table_name}'")

    except Exception as e:
        print(f"Skipped {file_name}: {e}")

conn.close()
print("All raw files processed.")
