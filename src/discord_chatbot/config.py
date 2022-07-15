import os

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from pydantic import BaseSettings

from myloguru.my_loguru import get_logger


# constants
DISCORD_BASE_URL: str = f'https://discord.com/api/v9/channels/'


class Settings(BaseSettings):
    TELEBOT_TOKEN: str
    ADMIN: str
    PARSING_TOKEN: str
    LOGGING_LEVEL: int = 20
    DEBUG: bool = False
    VOCABULARY_PATH_FILE: str = "vocabulary.txt"
    TOKENS_PATH_FILE: str = "tokens.txt"
    PROXIES_PATH_FILE: str = "proxies.txt"
    PARSED_PATH_FILE: str = "parsed.txt"
    MESSAGES_COUNT: int = 1000
    MIN_PAUSE: int = 1
    MAX_PAUSE: int = 3600
    PHRASE_RANDOM: bool = False


settings = Settings(_env_file='.env', _env_file_encoding='utf-8')

# logger
if not os.path.exists('./logs'):
    os.mkdir("./logs")
logger = get_logger(level=settings.LOGGING_LEVEL)

# configure bot
bot = Bot(token=settings.TELEBOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
