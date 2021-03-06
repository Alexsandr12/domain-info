import mysql.connector
from mysql.connector import Error
from typing import List

from exceptions import MySqlError
from config import HOST, USER, PASSWORD, DATABASE

method_conn = mysql.connector.connect(
    host=HOST, user=USER, password=PASSWORD, database=DATABASE
)

method_cursor = method_conn.cursor()
create_table_data = """
CREATE TABLE IF NOT EXISTS used_methods (
id INT AUTO_INCREMENT,
domain TEXT NOT NULL,
datetime TIMESTAMP NOT NULL,
methods TEXT NOT NULL,
success BOOL NOT NULL,
PRIMARY KEY (id)
)
"""

"""try:
    method_cursor.execute(create_table_data)
    method_conn.commit()
    print("Таблица создана")
except Error as e:
    print(e)"""


def check_connect_sql() -> None:
    """Проверка подключения к mariadb"""
    try:
        method_conn.ping()
    except mysql.connector.errors.InterfaceError:
        raise MySqlError


def rec_method_status_sql(dname: str, method: str, success_value: bool):
    """Запись информцаии о статусе выполнения метода

    Args:
        dname: домен
        method: название метода
        success_value: статус выполнения метода
    """
    query = """INSERT INTO used_methods
        ( domain, methods, success)
        VALUES ( %s, %s, %s)"""
    method_cursor.execute(query, (dname, method, success_value))
    method_conn.commit()


def get_all_data_sql() -> List[tuple]:
    """Получение всех данных из sql

    Return:
        List[tuple]: список со всеми строками таблицы
    """
    query = "SELECT * FROM used_methods"

    try:
        method_cursor.execute(query)
    except mysql.connector.errors.DatabaseError:
        raise MySqlError

    return method_cursor.fetchall()
