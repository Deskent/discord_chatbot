"""Модуль с основными обработчиками команд и сообщений"""
import asyncio
import random

from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext

from discord_bot import DiscordBot, ParserBot
from states import UserStates
from utils import check_is_int
from keyboards import StartMenu
from config import logger, Dispatcher, bot, settings


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
async def link_request_handler(message: Message, state: FSMContext) -> None:
    """
    Asks link for guild/channel
    """
    silent: bool = message.text == StartMenu.silent or message.text == StartMenu.parsing_silent
    await message.answer(
        "Введите ссылку на канал в виде: "
        "https://discord.com/channels/932034587264167975/932034858906401842",
        reply_markup=StartMenu.cancel_keyboard(),
        disable_web_page_preview=True
    )
    states_ = {
        StartMenu.silent: UserStates.normal_start,
        StartMenu.start: UserStates.normal_start,
        StartMenu.parsing: UserStates.parse_start,
        StartMenu.parsing_silent: UserStates.parse_start
    }
    await states_[message.text].set()
    await state.update_data(silent=silent)


@logger.catch
async def menu_selector_message(message: Message, state: FSMContext) -> None:
    """"""
    working_mode: str = await state.get_state()
    working_mode: str = working_mode.strip().split(':')[-1]
    try:
        guild, channel = message.text.rsplit('/', maxsplit=3)[-2:]
    except ValueError as err:
        logger.error(f"ValueError: {err}")
        guild: str = ''
        channel: str = ''
    guild: int = check_is_int(guild)
    channel: int = check_is_int(channel)
    if not all((guild, channel)):
        await message.answer(
            "Проверьте ссылку на канал и попробуйте ещё раз.",
            reply_markup=StartMenu.cancel_keyboard())
        return
    await UserStates.in_work.set()
    current_state: str = await state.get_state()
    state_data: dict = await state.get_data()
    silent: bool = state_data.get('silent', False)
    await _send_message(
        message=message,
        silent=silent,
        text=f'Начинаю работу.',
        reply_markup=StartMenu.cancel_keyboard()
    )
    workers = {
        'normal_start': DiscordBot(channel=channel),
        'parse_start': ParserBot(channel=channel, parse_channel=channel),

    }
    worker: 'DiscordBot' = workers[working_mode]
    while current_state == UserStates.in_work.state:
        delay: int = random.randint(settings.MIN_PAUSE, settings.MAX_PAUSE)
        result_data: dict = await worker.start()
        result: dict = result_data.get('result')
        if result:
            text = (
                f"\nПользователь {result.get('author', {}).get('username')}"
                f"\nотправил: [{result.get('content')}]"
                f"\nв канал {result.get('channel_id')}"
            )
            await _send_message(
                message=message,
                silent=silent,
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
        logger.debug(current_state)

    await state.finish()

    await _send_message(message, silent, text=f'Закончил работу.', reply_markup=StartMenu.keyboard())


@logger.catch
async def _send_message(message: Message, silent: bool, text: str, reply_markup):
    if not silent:
        await message.answer(text, reply_markup=reply_markup)


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
        StartMenu.start, StartMenu.silent, StartMenu.parsing, StartMenu.parsing_silent
    ]))
    dp.register_message_handler(menu_selector_message, state=UserStates.normal_start)
    dp.register_message_handler(menu_selector_message, state=UserStates.parse_start)
    dp.register_message_handler(default_message)
