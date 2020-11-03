import mysql.connector
from mysql.connector import Error


conn = mysql.connector.connect(
    host="localhost", user="alexandr", password="1", database="mysqltest"
)

cursor = conn.cursor()
create_table_data = """
CREATE TABLE IF NOT EXISTS used_methods (
id INT AUTO_INCREMENT,
domain TEXT NOT NULL
date DATE NOT NULL,
time TIMESTAMP NOT NULL,
methods TEXT NOT NULL,
success BOOL NOT NULL
PRIMARY KEY (id)
)
"""
try:
    cursor.execute(create_table_data)
    conn.commit()
    print("Таблица создана")
except Error as e:
    print(f"ебучая ошибка {e}")
