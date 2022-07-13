#!/usr/local/bin/python
# -*- coding: UTF-8 -*-

import datetime

from aiogram import executor

from config import dp, logger
from cancel_handler import cancel_register_handlers
from main_handlers import main_register_handlers
from errors_reporter import MessageReporter


cancel_register_handlers(dp=dp)
main_register_handlers(dp=dp)


@logger.catch
async def on_startup(_) -> None:
    """Функция выполняющаяся при старте бота."""

    text: str = (
        f"ChatBot started:"
    )

    await MessageReporter.send_report_to_admins(text=text)
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


if __name__ == '__main__':
    start_bot()
