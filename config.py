import os

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from pydantic import BaseSettings

from myloguru.my_loguru import get_logger


# Constants
DISCORD_BASE_URL: str = f'https://discord.com/api/v9/channels/'
# flag for saving files
SAVING: bool = False


class Settings(BaseSettings):
    LOGGING_LEVEL: int = 20
    TELEBOT_TOKEN: str = ''
    PROXY_USER: str = ''
    PROXY_PASSWORD: str = ''
    DEBUG: bool = False
    VOCABULARY_PATH_FILE: str = ""
    TOKENS_PATH_FILE: str = ""
    PROXIES_PATH_FILE: str = ""
    ADMIN: str = ''


settings = Settings(_env_file='.env', _env_file_encoding='utf-8')

admins_list = [settings.ADMIN]

# logger
if not os.path.exists('./logs'):
    os.mkdir("./logs")
logger = get_logger(level=settings.LOGGING_LEVEL)

# configure bot
bot = Bot(token=settings.TELEBOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
