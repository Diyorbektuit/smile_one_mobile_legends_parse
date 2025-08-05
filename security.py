import os
from dotenv import load_dotenv
load_dotenv()


class Security:
    DATABASE_URL: str = os.getenv('DATABASE_URL', "sqlite+aiosqlite:///./test.db")
    X_API_KEY: str = os.getenv('X_API_KEY')
    WK_EMAIL: str = os.getenv('WK_EMAIL')
    WK_PASSWORD: str = os.getenv('WK_PASSWORD')

SECURITY = Security()
