import psycopg
from psycopg.rows import dict_row
import os





def get_db_connection():
    return psycopg.connect(
        host="127.0.0.1",
        port=5432,
        dbname="taskhub",
        user="taskhub_user",
        password=os.environ["TASKHUB_DB_PASSWORD"],
        row_factory=dict_row
    )
