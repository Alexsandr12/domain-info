import psycopg2
from typing import List

from exceptions import MySqlError
from config import DSN


class SqlHandler:
    def __init__(self):
        self.conn = psycopg2.connect(DSN)

    def __del__(self):
        self.conn.close()

    def check_connect_sql(self) -> None:
        """Проверка подключения к postgresql"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT 1")
        except (psycopg2.InterfaceError, psycopg2.OperationalError):
            raise MySqlError

    def rec_method_status_sql(self, dname: str, method: str, success_value: bool):
        """Запись информцаии о статусе выполнения метода

        Args:
            dname: домен
            method: название метода
            success_value: статус выполнения метода
        """
        query = """INSERT INTO used_methods
            ( domain, methods, success)
            VALUES ( %s, %s, %s)"""

        cursor = self.conn.cursor()
        cursor.execute(query, (dname, method, success_value))
        self.conn.commit()

    def get_all_data_sql(self) -> List[tuple]:
        """Получение всех данных из sql

        Return:
            List[tuple]: список со всеми строками таблицы
        """
        query = "SELECT * FROM used_methods"
        cursor = self.conn.cursor()

        try:
            cursor.execute(query)
        except (psycopg2.InterfaceError, psycopg2.OperationalError):
            raise MySqlError

        return cursor.fetchall()


sql = SqlHandler()
