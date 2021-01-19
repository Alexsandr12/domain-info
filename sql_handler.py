import mysql.connector
from mysql.connector import Error
from typing import List

from projectexception import BdErrors
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
    #print("Таблица создана")
except Error as e:
    print(e)"""


def check_connect_mariadb():
    """Проверка подключения к mariadb"""
    try:
        method_conn.ping()
    except mysql.connector.errors.InterfaceError:
        raise BdErrors


def rec_method_status_mariadb(dname: str, method: str, success_value: bool):
    """Запись информцаии о статусе выполнения метода

    :param
        dname: домен
        method: название метода
        success_value: статус выполнения метода
    """
    query = f"""INSERT INTO used_methods 
        ( domain, methods, success) 
        VALUES ( %s, %s, %s)"""
    method_cursor.execute(query, (dname, method, success_value))
    method_conn.commit()


def get_all_data_mariadb() -> List[tuple]:
    """Получение всех данных из таблицы used_methods

    :return:
        List[tuple]: список со всеми строками таблицы
    """
    query = f"SELECT * FROM used_methods"
    method_cursor.execute(query)
    return method_cursor.fetchall()
