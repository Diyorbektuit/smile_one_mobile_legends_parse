import os
from dotenv import load_dotenv
load_dotenv()


class Security:
    DATABASE_URL: str = os.getenv('DATABASE_URL', "sqlite+aiosqlite:///./test.db")
    WK_EMAIL: str = os.getenv('WK_EMAIL')
    WK_PASSWORD: str = os.getenv('WK_PASSWORD')

SECURITY = Security()
