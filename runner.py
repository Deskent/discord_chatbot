import datetime

from aiogram import executor

from config import dp, logger, settings
from handlers import main_register_handlers
from keyboards import StartMenu
from utils import send_message_to_user


main_register_handlers(dp=dp)


@logger.catch
async def on_startup(_) -> None:
    """Функция выполняющаяся при старте бота."""

    text: str = (
        f"ChatBot started:"
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


@logger.catch
def start_bot() -> None:
    """Инициализация и старт бота"""

    executor.start_polling(
        dispatcher=dp,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
    )
