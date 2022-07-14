from dataclasses import dataclass
from typing import Union

from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardRemove
)

from config import logger


def default_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        resize_keyboard=True,
        one_time_keyboard=True,
        row_width=3
    )


@dataclass(frozen=True)
class BaseMenu:
    cancel_key: str = 'Отмена'

    @classmethod
    @logger.catch
    def keyboard(cls) -> Union[ReplyKeyboardMarkup, InlineKeyboardMarkup]:
        """Возвращает кнопочку Отмена"""

        return default_keyboard().add(KeyboardButton(cls.cancel_key))

    @classmethod
    @logger.catch
    def cancel_keyboard(cls):
        return BaseMenu.keyboard()


@dataclass(frozen=True)
class StartMenu(BaseMenu):
    """Стандартное пользовательское меню"""

    start: str = 'Start'
    silent: str = 'Start (mute)'
    parsing: str = 'Parsing'
    parsing_silent: str = 'Parsing (mute)'

    @classmethod
    @logger.catch
    def keyboard(cls) -> 'ReplyKeyboardMarkup':
        """Возвращает кнопочки меню для канала из списка"""

        return default_keyboard().add(
            KeyboardButton(cls.start),
            KeyboardButton(cls.silent),
            KeyboardButton(cls.parsing),
            KeyboardButton(cls.parsing_silent),
        )
