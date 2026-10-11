import os

import psycopg2
from dotenv import load_dotenv


def get_connection():
    load_dotenv()
    return psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
    )


def call_sql_loader():
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        with open("../sql/carga.sql", "r", encoding="utf-8") as f:
            cur.execute(f.read())
        tables = {
            "conditions": "conditions.csv",
            "encounters": "encounters.csv",
            "medications": "medications.csv",
            "observations": "observations.csv",
            "patients": "patients.csv",
        }

        print("|\tTable\t|\tRow count\t|")

        for table_name, filename in tables.items():
            copy_sql = f"COPY {table_name} FROM STDIN WITH (FORMAT csv, HEADER true, DELIMITER ',', NULL '')"
            with open(f"../data/{filename}", "r", encoding="utf-8") as f:
                cur.copy_expert(sql=copy_sql, file=f)
            cur.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cur.fetchone()[0]
            print("-" * 41)
            print(f"|\t{table_name}\t|\t{count}\t|")

        conn.commit()
        return True

    except psycopg2.Error as e:
        print(f"Failed to load database: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()
