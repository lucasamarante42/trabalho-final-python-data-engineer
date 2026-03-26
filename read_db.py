import sqlite3
import pandas as pd

def main():
    conn = sqlite3.connect("assets/database.db")

    df = pd.read_sql("SELECT * FROM users", conn)

    print("\n=== DADOS DO BANCO ===\n")
    print(df)
    print("\nTotal de registros:", len(df))

    conn.close()


if __name__ == "__main__":
    main()