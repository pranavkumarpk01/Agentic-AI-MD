from pathlib import Path
from dotenv import load_dotenv
import sqlite3
import json
import os

load_dotenv()

CREWAI_DIR = Path(
    os.getenv("CREWAI_STORAGE_DIR")
)

#os.environ["CREWAI_STORAGE_DIR"] = "/Users/pranav/Documents/Agentic AI/Crew-AI/.crewai"


print("\n" + "=" * 80)
print("CREWAI STORAGE LOCATION")
print("=" * 80)
print(CREWAI_DIR)

if not CREWAI_DIR.exists():
    print("CrewAI directory not found.")
    exit()

print("\n")
print("=" * 80)
print("FILES")
print("=" * 80)

for root, dirs, files in os.walk(CREWAI_DIR):
    level = root.replace(str(CREWAI_DIR), "").count(os.sep)
    indent = " " * 4 * level
    print(f"{indent}{os.path.basename(root)}/")

    subindent = " " * 4 * (level + 1)

    for file in files:
        full_path = os.path.join(root, file)

        try:
            size = os.path.getsize(full_path)
            print(f"{subindent}{file} ({size:,} bytes)")
        except:
            print(f"{subindent}{file}")

print("\n")
print("=" * 80)
print("SQLITE DATABASES")
print("=" * 80)

for db_file in CREWAI_DIR.rglob("*.db"):

    print("\n")
    print("-" * 80)
    print(db_file)
    print("-" * 80)

    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type='table'
        """)

        tables = cursor.fetchall()

        if not tables:
            print("No tables found.")
            continue

        for (table_name,) in tables:

            print(f"\nTABLE: {table_name}")

            try:
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()

                print("Columns:")
                for col in columns:
                    print(
                        f"  {col[1]} ({col[2]})"
                    )

                cursor.execute(
                    f"SELECT * FROM {table_name} LIMIT 5"
                )

                rows = cursor.fetchall()

                print("\nSample Rows:")

                for row in rows:
                    print(row)

            except Exception as e:
                print(f"Error reading table: {e}")

        conn.close()

    except Exception as e:
        print(f"Failed opening DB: {e}")

print("\n")
print("=" * 80)
print("JSON FILES")
print("=" * 80)

for json_file in CREWAI_DIR.rglob("*.json"):

    print("\n")
    print("-" * 80)
    print(json_file)
    print("-" * 80)

    try:
        with open(json_file, "r") as f:
            data = json.load(f)

        print(
            json.dumps(
                data,
                indent=2
            )[:5000]
        )

    except Exception as e:
        print(e)

print("\n")
print("=" * 80)
print("DONE")
print("=" * 80)