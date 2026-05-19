import os
from mysql.connector import connect
from dotenv import load_dotenv

load_dotenv()

_CONFIG = dict(
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", ""),
    database=os.getenv("DB_NAME", "hospital"),
)


def get_connection():
    return connect(**_CONFIG)
