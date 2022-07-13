from request_classes import PostRequest, DataStructure
from config import logger, DISCORD_BASE_URL
from vocabulary import Vocabulary


class MessageSender(PostRequest):
    """Отправляет сообщение в дискорд-канал в ответ на сообщение
    связанного токена
    Возвращает сообщение об ошибке или об успехе"""

    def __init__(self, token: str, proxy: str, channel: int):
        super().__init__(token)
        self.token: str = token
        self.proxy: str = proxy
        self.channel: int = channel
        self._data_for_send: dict = {}
        self.text_to_send: str = ''

    @logger.catch
    async def send_message_to_discord(self) -> dict:
        """Отправляет данные в канал дискорда, возвращает результат отправки."""
        self.text_to_send = Vocabulary.get_message()
        text: str = (
            f"send to channel: [{self.channel}]:\t"
            f"message text: [{self.text_to_send}]"
        )
        logger.info(text)
        await self.__get_data_for_send()
        self.url = DISCORD_BASE_URL + f'{self.channel}/messages?'
        result: 'DataStructure' = await self.send_request()
        return result.data if result else {}

    @logger.catch
    async def __get_data_for_send(self) -> None:

        if not self.text_to_send:
            logger.warning("\n\t\tMessage_receiver.__prepare_data: no text for sending.\n")
            return
        self._data_for_send = {
            "content": self.text_to_send,
            "tts": "false"
        }
