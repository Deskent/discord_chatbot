import datetime
import os

from aiogram import executor

from discord_chatbot.config import dp, logger, settings
from discord_chatbot.handlers import main_register_handlers
from discord_chatbot.keyboards import StartMenu
from discord_chatbot.utils import send_message_to_user


main_register_handlers(dp=dp)


@logger.catch
async def on_startup(_) -> None:
    """Функция выполняющаяся при старте бота."""

    text: str = (
        f"ChatBot started."
    )

    await send_message_to_user(text=text, telegram_id=settings.ADMIN, keyboard=StartMenu.keyboard())
    logger.success(
        f'Bot started at: {datetime.datetime.now()}'
        f'\nBOT POLLING ONLINE')


@logger.catch
async def on_shutdown(dp) -> None:
    """Действия при отключении бота."""
    logger.warning("BOT shutting down.")
    await dp.storage.wait_closed()
    logger.warning("BOT down.")


def _creating_files():
    print('Creating files...')

    files = (
        settings.TOKENS_PATH_FILE, settings.VOCABULARY_PATH_FILE, settings.PROXIES_PATH_FILE,
        settings.PARSED_PATH_FILE, settings.VOCABULARY_PATH_FILE
    )
    for filename in files:
        if not os.path.exists(filename):
            open(filename, 'a').close()
    print('Creating files... OK')


@logger.catch
def start_bot() -> None:
    """Инициализация и старт бота"""

    _creating_files()
    executor.start_polling(
        dispatcher=dp,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
    )
