"""Модуль с основными обработчиками команд и сообщений"""
import asyncio
import random
from typing import Tuple

from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext

from discord_chatbot.discord_bot import DiscordBot, Parser
from discord_chatbot.states import UserStates
from discord_chatbot.utils import check_is_int
from discord_chatbot.keyboards import StartMenu
from discord_chatbot.config import logger, Dispatcher, bot, settings


@logger.catch
async def callback_cancel_handler(callback: CallbackQuery, state: FSMContext) -> None:
    """Ловит коллбэк инлайн кнопки Отмена и вызывает обработик для нее"""

    await send_cancel_message(telegram_id=str(callback.from_user.id), state=state)
    await callback.answer()


@logger.catch
async def message_cancel_handler(message: Message, state: FSMContext) -> None:
    """Ловит сообщение или команду отмена, Отмена, cancel и вызывает обработик для нее"""

    await send_cancel_message(telegram_id=str(message.from_user.id), state=state)


@logger.catch
async def send_cancel_message(telegram_id: str, state: FSMContext) -> None:
    """
    Отменяет текущие запросы и сбрасывает состояние.
    Ставит пользователя в нерабочее состояние.
    Обработчик команды /cancel, /Отмена, кнопки Отмена и инлайн кнопки Отмена
    """
    await bot.send_message(
        chat_id=telegram_id,
        text="Вы отменили текущую команду.",
        reply_markup=StartMenu.keyboard()
    )
    logger.debug(f"\n\t{telegram_id}: canceled command.")
    await state.finish()


@logger.catch
async def hello_handler(message: Message):

    await message.answer("Добро пожаловать.", reply_markup=StartMenu.keyboard())


@logger.catch
async def pause_request_handler(message: Message) -> None:
    """
    Asks pause
    """

    await message.answer(
        "Введите диапазон паузы между сообщениями в формате 120-280",
        reply_markup=StartMenu.cancel_keyboard(),
    )
    await UserStates.set_pause.set()


@logger.catch
async def set_pause_handler(message: Message, state: FSMContext) -> None:
    """
    Set pause
    """

    pause = message.text.split('-')
    min_pause: int = check_is_int(pause[0])
    max_pause: int = check_is_int(pause[1])
    if not all((min_pause, max_pause)):
        await message.answer(
            "Ошибка ввода. Введите диапазон паузы между сообщениями в формате 120-280",
            reply_markup=StartMenu.cancel_keyboard(),
        )
        return
    settings.MIN_PAUSE = min_pause
    settings.MAX_PAUSE = max_pause
    await message.answer(
        f"Диапазон установлен: {min_pause}-{max_pause}",
        reply_markup=StartMenu.keyboard(),
    )
    await state.finish()


@logger.catch
async def link_request_handler(message: Message) -> None:
    """
    Asks link for guild/channel
    """

    await message.answer(
        "Введите ссылку на канал в виде: "
        "https://discord.com/channels/932034587264167975/932034858906401842",
        reply_markup=StartMenu.cancel_keyboard(),
        disable_web_page_preview=True
    )
    states_ = {
        StartMenu.start_parsed: UserStates.normal_start,
        StartMenu.start_vocabulary: UserStates.normal_start,
        StartMenu.parsing: UserStates.parsing,
    }
    await states_[message.text].set()


@logger.catch
def _get_guild_and_channel(message: Message) -> Tuple[int, int]:
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
    """"""

    guild, channel = _get_guild_and_channel(message)
    if not all((guild, channel)):
        await message.answer(
            "Проверьте ссылку на канал и попробуйте ещё раз.",
            reply_markup=StartMenu.cancel_keyboard())
        return
    parse_result: dict = await Parser(channel=channel).parse_data()
    count = parse_result['result']
    await message.answer(
        f"Спарсил {count} сообщений из чата {channel}",
        reply_markup=StartMenu.keyboard()
    )
    await state.finish()


@logger.catch
async def _get_vocabulary(state: FSMContext) -> str:
    working_mode: str = await state.get_state()
    working_mode: str = working_mode.strip().split(':')[-1]
    vocabulary: str = settings.VOCABULARY_PATH_FILE
    if working_mode == UserStates.parsed_start.state:
        vocabulary = settings.PARSED_PATH_FILE
    return vocabulary


@logger.catch
async def menu_selector_message(message: Message, state: FSMContext) -> None:
    """"""

    vocabulary: str = await _get_vocabulary(state)
    guild, channel = _get_guild_and_channel(message)
    if not all((guild, channel)):
        await message.answer(
            "Проверьте ссылку на канал и попробуйте ещё раз.",
            reply_markup=StartMenu.cancel_keyboard())
        return
    await message.answer(
        text=f'Начинаю работу.',
        reply_markup=StartMenu.cancel_keyboard()
    )
    await UserStates.in_work.set()
    await run(message, state, channel, vocabulary)
    await state.finish()
    await message.answer(text=f'Закончил работу.', reply_markup=StartMenu.keyboard())


async def run(message: Message, state: FSMContext, channel: int, vocabulary: str):
    current_state: str = await state.get_state()

    while current_state == UserStates.in_work.state:
        delay: int = random.randint(settings.MIN_PAUSE, settings.MAX_PAUSE)
        result_data: dict = await DiscordBot(channel=channel, vocabulary=vocabulary).start()
        result: dict = result_data.get('result')
        if result:
            text = (
                f"\nПользователь {result.get('author', {}).get('username')}"
                f"\nотправил: [{result.get('content')}]"
                f"\nв канал {result.get('channel_id')}"
            )
            await message.answer(
                text=f'Результат выполнения: {text}',
                reply_markup=StartMenu.cancel_keyboard()
            )
        else:
            error: str = result_data.get('error')
            await message.answer(f'Ошибка: {error}', reply_markup=StartMenu.keyboard())
            break
        logger.debug(f"Sleep: {delay} seconds")
        await asyncio.sleep(delay)
        current_state: str = await state.get_state()


@logger.catch
async def default_message(message: Message) -> None:
    """Ответ на любое необработанное действие активного пользователя."""

    await message.answer(f'Команда не распознана.', reply_markup=StartMenu.keyboard())


@logger.catch
def main_register_handlers(dp: Dispatcher) -> None:
    """
    Регистратор для функций данного модуля
    """
    dp.register_message_handler(message_cancel_handler, commands=['отмена', 'cancel'], state="*")
    dp.register_message_handler(message_cancel_handler, Text(
        startswith=[StartMenu.cancel_key], ignore_case=True), state="*")
    dp.register_message_handler(hello_handler, commands=["start"])
    dp.register_message_handler(link_request_handler, Text(equals=[
        StartMenu.start_vocabulary, StartMenu.parsing, StartMenu.start_parsed
    ]))
    dp.register_message_handler(pause_request_handler, Text(equals=[StartMenu.pause]))
    dp.register_message_handler(set_pause_handler, state=UserStates.set_pause)
    dp.register_message_handler(menu_selector_message, state=UserStates.parsed_start)
    dp.register_message_handler(menu_selector_message, state=UserStates.normal_start)
    dp.register_message_handler(parser_handler, state=UserStates.parsing)
    dp.register_message_handler(default_message)
