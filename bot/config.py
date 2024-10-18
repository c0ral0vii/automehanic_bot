from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

BOT_TOKEN=os.environ.get("BOT_TOKEN")
DB_HOST=os.environ.get("DB_HOST")
DB_NAME=os.environ.get("DB_NAME")
DB_PASSWORD=os.environ.get("DB_PASSWORD")
DB_PORT=os.environ.get("DB_PORT")
DB_USER=os.environ.get("DB_USER")
ADMINS_LIST = os.environ.get("ADMINS_LIST", "")
ADMINS_LIST = list(map(int, ADMINS_LIST.split(","))) if ADMINS_LIST else []
