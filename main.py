import os
import sys

import psycopg
from PyQt6.QtWidgets import QApplication

from backend import Backend
from frontend import Controller


def load_env():
    with open(".env", "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if line == "" or line.startswith("#"):
                continue

            key, value = line.split("=", 1)
            os.environ[key] = value


def main():
    load_env()

    connection = psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

    app = QApplication(sys.argv)

    backend = Backend(connection)
    controller = Controller(backend)
    controller.login_window.show()

    app.exec()

    connection.close()


if __name__ == "__main__":
    main()