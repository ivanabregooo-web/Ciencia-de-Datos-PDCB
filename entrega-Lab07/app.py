import os

import psycopg2
from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/")
def test_db_connection():
    db_host = os.environ.get("DB_HOST", "db")
    db_user = os.environ.get("DB_USER")
    db_password = os.environ.get("DB_PASSWORD")
    db_name = os.environ.get("DB_NAME")

    try:
        conn = psycopg2.connect(
            host=db_host, user=db_user, password=db_password, database=db_name
        )

        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        return jsonify(
            {
                "status": "success",
                "message": "Conectado a la base de datos :)",
                "database_version": db_version,
            }
        )

    except psycopg2.Error as e:
        return jsonify(
            {
                "status": "error",
                "message": "NO conectado a la base de datos :(",
                "error_details": str(e),
            }
        ), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0")
