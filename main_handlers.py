"""Модуль с основными обработчиками команд и сообщений"""
import asyncio

from aiogram.types import Message
from aiogram.dispatcher.filters import Text

from keyboards_classes import StartMenu, BaseMenu
from config import logger, Dispatcher
from discord_bot import DiscordBot
from states import UserStates
from aiogram.dispatcher import FSMContext
from utils import Frequency


@logger.catch
async def hello_handler(message: Message):

    await message.answer("Добро пожаловать.", reply_markup=StartMenu.keyboard())


@logger.catch
async def frequency_request_handler(message: Message):
    await message.answer("Введите частоту отправки сообщений.", reply_markup=BaseMenu.keyboard())
    await UserStates.frequency_post.set()


@logger.catch
async def frequency_check_handler(message: Message, state: FSMContext):
    a = await state.get_state()
    logger.info(a)
    frequency = message.text
    if frequency.isdigit():
        Frequency.save_frequency(frequency)
        await message.answer(
            f"Частота отправки сообщений установлена в {frequency} сек.",
            reply_markup=StartMenu.keyboard()
        )
        await state.finish()
        return
    await message.answer('Вы ввели не число. Введите число', reply_markup=StartMenu.keyboard())


@logger.catch
async def menu_selector_message(message: Message, state: FSMContext) -> None:
    """"""
    try:
        frequency: int = Frequency.load_frequency()
    except FileNotFoundError:
        await message.answer('Задайте частоту отправки сообщений.', reply_markup=StartMenu.keyboard())
        await state.finish()
        return

    await UserStates.in_work.set()
    current_state: str = await state.get_state()
    while current_state == 'UserStates:in_work':
        result_data: dict = await DiscordBot().start()
        result: dict = result_data.get('result')
        if result:
            text = (
                f"\nПользователь {result.get('author', {}).get('username')}"
                f"\nотправил: [{result.get('content')}]"
                f"\nв канал {result.get('channel_id')}"
            )

            await message.answer(f'Результат выполнения: {text}', reply_markup=StartMenu.keyboard())
        else:
            error: str = result_data.get('error')
            await message.answer(f'Ошибка: {error}', reply_markup=StartMenu.keyboard())
        await asyncio.sleep(frequency)
        current_state: str = await state.get_state()
        logger.info(current_state)


@logger.catch
async def default_message(message: Message) -> None:
    """Ответ на любое необработанное действие активного пользователя."""

    await message.answer(f'Команда не распознана', reply_markup=StartMenu.keyboard())


@logger.catch
def main_register_handlers(dp: Dispatcher) -> None:
    """
    Регистратор для функций данного модуля
    """

    dp.register_message_handler(hello_handler, commands=["start"])
    dp.register_message_handler(frequency_request_handler, Text(
        equals=[StartMenu.set_frequency]))
    dp.register_message_handler(frequency_check_handler, state=UserStates.frequency_post)
    dp.register_message_handler(menu_selector_message, Text(
        equals=[StartMenu.start, StartMenu.stop]))
    dp.register_message_handler(default_message)
