import os
from mysql.connector import pooling
from dotenv import load_dotenv

load_dotenv()

_CONFIG = dict(
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", ""),
    database=os.getenv("DB_NAME", "hospital"),
)

_pool = pooling.MySQLConnectionPool(pool_name="novacare", pool_size=5, **_CONFIG)


def get_connection():
    return _pool.get_connection()
