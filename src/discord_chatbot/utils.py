import aiogram.utils.exceptions

from discord_chatbot.config import logger, bot


@logger.catch
def check_is_int(text: str) -> int:
    """Проверяет что в строке пришло положительное число и возвращает его обратно если да"""

    if text.isdigit():
        if int(text) > 0:
            return int(text)

    return 0


@logger.catch
async def send_message_to_user(text: str, telegram_id: str, keyboard=None) -> None:
    """Отправляет сообщение пользователю в телеграм"""

    params: dict = {
        "chat_id": telegram_id,
        "text": text
    }
    if keyboard:
        params.update(reply_markup=keyboard)
    try:
        await bot.send_message(**params)
    except aiogram.utils.exceptions.ChatNotFound:
        logger.error(f"Chat {telegram_id} not found")
    except aiogram.utils.exceptions.BotBlocked as err:
        logger.error(f"Пользователь {telegram_id} заблокировал бота {err}")
    except aiogram.utils.exceptions.CantInitiateConversation as err:
        logger.error(f"Не смог отправить сообщение пользователю {telegram_id}. {err}")
    logger.success(f"Send_message_to_user: {telegram_id}: {text}")
