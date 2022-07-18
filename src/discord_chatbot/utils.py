import aiogram.utils.exceptions

from discord_chatbot.config import logger, bot


@logger.catch
def check_is_int(text: str) -> int:
    """Returns number if string is positive digit else 0"""

    if text.isdigit():
        if int(text) > 0:
            return int(text)

    return 0


@logger.catch
async def send_message_to_user(text: str, telegram_id: str, keyboard=None) -> None:
    """Sends a message to a user in Telegram"""

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
        logger.error(f"User {telegram_id} block the bot {err}")
    except aiogram.utils.exceptions.CantInitiateConversation as err:
        logger.error(f"Can`t send message to user {telegram_id}. {err}")
    logger.success(f"Send_message_to_user: {telegram_id}: {text}")
