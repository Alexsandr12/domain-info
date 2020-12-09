import mysql.connector
from mysql.connector import Error


from utilits import MyException

method_conn = mysql.connector.connect(
    host="localhost", user="alexandr", password="1", database="mysqltest"
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


def add_data_in_mariadb(dname, method, success_value):
    query = f"""INSERT INTO used_methods 
        ( domain, methods, success) 
        VALUES ( %s, %s, %s)"""
    method_cursor.execute(query, (dname, method, success_value))
    method_conn.commit()

