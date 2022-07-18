"""Модуль с основными обработчиками команд и сообщений"""
import random
import time
from typing import Tuple

from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext

from discord_chatbot.discord_bot import DiscordBot, Parser
from discord_chatbot.states import UserStates
from discord_chatbot.utils import check_is_int
from discord_chatbot.keyboards import StartMenu
from discord_chatbot.config import logger, Dispatcher, bot, settings
from discord_chatbot._resources import __version__ as VERSION


@logger.catch
async def callback_cancel_handler(callback: CallbackQuery, state: FSMContext) -> None:
    """Cancel current state and send message for user"""

    await _send_cancel_message(telegram_id=callback.from_user.id, state=state)
    await callback.answer()


@logger.catch
async def message_cancel_handler(message: Message, state: FSMContext) -> None:
    """Cancel current state and send message for user"""

    await _send_cancel_message(telegram_id=message.from_user.id, state=state)


@logger.catch
async def _send_cancel_message(telegram_id: int, state: FSMContext) -> None:
    """Cancel current state and send message for user"""

    text = "Вы отменили текущую команду."
    await bot.send_message(
        chat_id=telegram_id,
        text=text,
        reply_markup=StartMenu.keyboard()
    )
    logger.debug(f"\n\t{telegram_id}: canceled command.")
    await state.finish()


@logger.catch
async def hello_handler(message: Message):
    """
    Handler for /start command
    """

    text = f"Добро пожаловать.\nVersion: {VERSION}"
    await message.answer(text, reply_markup=StartMenu.keyboard())


@logger.catch
async def pause_request_handler(message: Message) -> None:
    """
    Asks pause range
    """
    text = "Введите диапазон паузы между сообщениями в формате 120-280"
    await message.answer(text, reply_markup=StartMenu.cancel_keyboard(), )
    await UserStates.set_pause.set()


@logger.catch
async def set_pause_handler(message: Message, state: FSMContext) -> None:
    """
    Set pause range
    """

    pause = message.text.split('-')
    min_pause: int = check_is_int(pause[0])
    max_pause: int = check_is_int(pause[1])
    if not all((min_pause, max_pause)):
        text = "Ошибка ввода. Введите диапазон паузы между сообщениями в формате 120-280"
        await message.answer(text, reply_markup=StartMenu.cancel_keyboard())
        return
    settings.MIN_PAUSE = min_pause
    settings.MAX_PAUSE = max_pause
    text = f"Диапазон установлен: {min_pause}-{max_pause}"
    await message.answer(text, reply_markup=StartMenu.keyboard())
    await state.finish()


@logger.catch
async def link_request_handler(message: Message) -> None:
    """
    Asks link for guild/channel
    """

    text = (
        "Введите ссылку на канал в виде:\n"
        "https://discord.com/channels/932034587264167975/932034858906401842"
    )
    await message.answer(
        text, reply_markup=StartMenu.cancel_keyboard(), disable_web_page_preview=True)
    states_ = {
        StartMenu.start_parsed: UserStates.normal_start,
        StartMenu.start_vocabulary: UserStates.normal_start,
        StartMenu.parsing: UserStates.parsing,
    }
    await states_[message.text].set()


@logger.catch
def _get_guild_and_channel(message: Message) -> Tuple[int, int]:
    """Returns guild and channel from link"""

    try:
        guild, channel = message.text.rsplit('/', maxsplit=3)[-2:]
    except ValueError as err:
        logger.error(f"ValueError: {err}")
        guild: str = ''
        channel: str = ''
    guild: int = check_is_int(guild)
    channel: int = check_is_int(channel)

    return guild, channel


@logger.catch
async def parser_handler(message: Message, state: FSMContext) -> None:
    """Parse messages from discord chat and save them to file"""

    guild, channel = _get_guild_and_channel(message)
    if not all((guild, channel)):
        text = "Проверьте ссылку на канал и попробуйте ещё раз."
        await message.answer(text, reply_markup=StartMenu.cancel_keyboard())
        return
    parse_result: dict = await Parser(channel=channel).parse_data()
    count: int = parse_result['result']
    text = f"Спарсил {count} сообщений из чата {channel}"
    await message.answer(text, reply_markup=StartMenu.keyboard())
    await state.finish()


@logger.catch
async def _get_vocabulary(state: FSMContext) -> str:
    """Returns vocabulary filename by mode"""

    working_mode: str = await state.get_state()
    working_mode: str = working_mode.strip().split(':')[-1]
    vocabulary: str = settings.VOCABULARY_PATH_FILE
    if working_mode == UserStates.parsed_start.state:
        vocabulary = settings.PARSED_PATH_FILE
    return vocabulary


@logger.catch
async def start_discord_bot_handler(message: Message, state: FSMContext) -> None:
    """Start discord bot"""

    vocabulary: str = await _get_vocabulary(state)
    guild, channel = _get_guild_and_channel(message)
    if not all((guild, channel)):
        text = "Проверьте ссылку на канал и попробуйте ещё раз."
        await message.answer(text, reply_markup=StartMenu.cancel_keyboard())
        return
    text = 'Начинаю работу.'
    await message.answer(text, reply_markup=StartMenu.cancel_keyboard())
    await UserStates.in_work.set()
    await _run(message, state, channel, vocabulary)
    await state.finish()
    text = 'Закончил работу.'
    await message.answer(text, reply_markup=StartMenu.keyboard())


async def _run(message: Message, state: FSMContext, channel: int, vocabulary: str):
    """Runs work loop for discord bot while state is equal in_work"""

    current_state: str = await state.get_state()
    discord_bot = DiscordBot(channel=channel, vocabulary=vocabulary)
    while current_state == UserStates.in_work.state:
        delay: int = random.randint(settings.MIN_PAUSE, settings.MAX_PAUSE)
        result_data: dict = await discord_bot.start()
        result: dict = result_data.get('result')
        if result:
            text_result = (
                f"\nПользователь {result.get('author', {}).get('username')}"
                f"\nотправил: [{result.get('content')}]"
                f"\nв канал {result.get('channel_id')}"
            )
            text = f'Результат выполнения: {text_result}'
            await message.answer(text, reply_markup=StartMenu.cancel_keyboard())
        else:
            text: str = result_data.get('error')
            text = f'Ошибка: {text}'
            await message.answer(text, reply_markup=StartMenu.keyboard())
            break
        logger.debug(f"Sleep: {delay} seconds")
        time.sleep(delay)
        current_state: str = await state.get_state()


@logger.catch
async def default_message(message: Message) -> None:
    """Default message"""

    text = 'Команда не распознана.'
    await message.answer(text, reply_markup=StartMenu.keyboard())


@logger.catch
def main_register_handlers(dp: Dispatcher) -> None:
    """Handlers register"""

    dp.register_message_handler(message_cancel_handler, commands=['отмена', 'cancel'], state="*")
    dp.register_message_handler(message_cancel_handler, Text(
        startswith=[StartMenu.cancel_key], ignore_case=True), state="*")
    dp.register_message_handler(hello_handler, commands=["start"])
    dp.register_message_handler(link_request_handler, Text(equals=[
        StartMenu.start_vocabulary, StartMenu.parsing, StartMenu.start_parsed
    ]))
    dp.register_message_handler(pause_request_handler, Text(equals=[StartMenu.pause]))
    dp.register_message_handler(set_pause_handler, state=UserStates.set_pause)
    dp.register_message_handler(start_discord_bot_handler, state=UserStates.parsed_start)
    dp.register_message_handler(start_discord_bot_handler, state=UserStates.normal_start)
    dp.register_message_handler(parser_handler, state=UserStates.parsing)
    dp.register_message_handler(default_message)
