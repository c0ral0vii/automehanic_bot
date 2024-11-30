from dotenv import load_dotenv, find_dotenv
import os

# это для сброса кэша у меня
for key in list(os.environ.keys()):
    if key.startswith("BOT_") or key.startswith("DB_") or key == "ADMINS_LIST":
        del os.environ[key]

load_dotenv(find_dotenv())

BOT_TOKEN = str(os.environ.get("BOT_TOKEN", ""))
DB_HOST = str(os.environ.get("DB_HOST", "db"))
DB_NAME = str(os.environ.get("DB_NAME", ""))
DB_PASSWORD = str(os.environ.get("DB_PASSWORD", "root"))
DB_PORT = str(os.environ.get("DB_PORT", "5432")  )
DB_USER = str(os.environ.get("DB_USER", "root"))
ADMINS_LIST = os.environ.get("ADMINS_LIST", "")
ADMINS_LIST = [
    int(admin.split("#")[0].strip()) for admin in ADMINS_LIST.split(",") if admin.split("#")[0].strip().isdigit()
]