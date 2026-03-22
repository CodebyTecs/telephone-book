import os
import sys

import psycopg

from backend import Backend
from cli import run_cli

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def load_env():
    env_path = os.path.join(BASE_DIR, ".env")
    with open(env_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if line == "" or line.startswith("#"):
                continue

            key, value = line.split("=", 1)
            os.environ[key] = value


def create_connection():
    return psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )


def main():
    load_env()
    connection = create_connection()
    backend = Backend(connection)

    try:
        if "--cli" in sys.argv:
            run_cli(backend)
            return

        from PyQt6.QtWidgets import QApplication
        from frontend import Controller

        app = QApplication(sys.argv)
        controller = Controller(backend)
        controller.login_window.show()
        app.exec()
    finally:
        connection.close()


if __name__ == "__main__":
    main()

