from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext

from keyboards_classes import StartMenu
from config import logger, Dispatcher, bot


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
def cancel_register_handlers(dp: Dispatcher) -> None:
    """
    Регистратор для функций данного модуля
    """

    dp.register_message_handler(message_cancel_handler, commands=['отмена', 'cancel'], state="*")
    dp.register_message_handler(message_cancel_handler, Text(
        startswith=[StartMenu.cancel_key, StartMenu.stop], ignore_case=True), state="*")
