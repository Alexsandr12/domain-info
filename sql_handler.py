import mysql.connector
from mysql.connector import Error

from utilits import MyException
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


def check_connect_mariadb():
    try:
        method_conn.ping()
    except mysql.connector.errors.InterfaceError:
        raise MyException


def rec_method_status_mariadb(dname, method, success_value):
    query = f"""INSERT INTO used_methods 
        ( domain, methods, success) 
        VALUES ( %s, %s, %s)"""
    method_cursor.execute(query, (dname, method, success_value))
    method_conn.commit()


def get_all_data_mariadb():
    query = f"SELECT * FROM used_methods"
    method_cursor.execute(query)
    return method_cursor.fetchall()
