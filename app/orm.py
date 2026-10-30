import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker

load_dotenv()

database_url = URL.create(
    drivername="postgresql+psycopg",
    username="taskhub_user",
    password=os.environ["TASKHUB_DB_PASSWORD"],
    host="127.0.0.1",
    port=5432,
    database=os.getenv("TASKHUB_DB_NAME", "taskhub"),
)

engine = create_engine(database_url)

SessionLocal = sessionmaker(bind=engine)
