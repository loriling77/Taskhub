import os
import psycopg
from psycopg.rows import dict_row

conn = psycopg.connect(
    host="127.0.0.1",
    port=5432,
    dbname="taskhub",
    user="taskhub_user",
    password=os.environ["TASKHUB_DB_PASSWORD"]
)

print("Connected to PostgreSQL!")

cur = conn.cursor(row_factory=dict_row)

cur.execute("SELECT id, title, status FROM tasks")

rows = cur.fetchall()

print(rows)

cur.close()

conn.close()