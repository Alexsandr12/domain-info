import psycopg2

from config import DSN


def create_table():
    conn = psycopg2.connect(DSN)
    create_table_data = """
    CREATE TABLE used_methods (
    id SERIAL PRIMARY KEY,
    domain CHARACTER VARYING(200) NOT NULL,
    datetime TIMESTAMP DEFAULT NOW(),
    methods CHARACTER VARYING(50) NOT NULL,
    success BOOLEAN NOT NULL
    );
    """
    cursor = conn.cursor()
    cursor.execute(create_table_data)
    conn.commit()
    conn.close()
    print("Таблица создана")


if __name__ == "__main__":
    create_table()
