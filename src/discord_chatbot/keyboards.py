from dataclasses import dataclass
from typing import Union

from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup
)

from discord_chatbot.config import logger


def default_keyboard() -> ReplyKeyboardMarkup:
    """Returns default keyboard"""

    return ReplyKeyboardMarkup(
        resize_keyboard=True,
        one_time_keyboard=True,
        row_width=3
    )


@dataclass(frozen=True)
class BaseMenu:
    """Base menu"""
    cancel_key: str = 'Отмена'

    @classmethod
    @logger.catch
    def keyboard(cls) -> Union[ReplyKeyboardMarkup, InlineKeyboardMarkup]:
        """Returns keyboard"""

        return default_keyboard().add(KeyboardButton(cls.cancel_key))

    @classmethod
    @logger.catch
    def cancel_keyboard(cls):
        """Returns cancel keyboard"""

        return BaseMenu.keyboard()


@dataclass(frozen=True)
class StartMenu(BaseMenu):
    """Standart menu"""

    start_vocabulary: str = 'Start from vocabulary.txt'
    start_parsed: str = 'Start from parsed.txt'
    parsing: str = 'Parsing from chat'
    pause: str = 'Set pause range'

    @classmethod
    @logger.catch
    def keyboard(cls) -> 'ReplyKeyboardMarkup':
        """Returns keyboard"""

        return default_keyboard().add(
            KeyboardButton(cls.start_vocabulary),
            KeyboardButton(cls.start_parsed),
            KeyboardButton(cls.parsing),
            KeyboardButton(cls.pause)
        )
