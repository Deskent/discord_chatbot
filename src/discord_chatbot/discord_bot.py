import os.path
import random
from typing import List, Dict

from discord_chatbot.requesters import PostRequest, GetRequest
from discord_chatbot.config import logger, settings, DISCORD_BASE_URL

from discord_chatbot.vocabulary import Vocabulary


class DiscordBot:
    """Send messages to channel from vocabulary

    Attributes
        channel: int

        vocabulary: str = ''

    Methods
        start
    """

    def __init__(self, channel: int, vocabulary: str):
        self._tokens: List[str] = []
        self._proxy: List[str] = []
        self.channel: int = channel
        self.vocabulary: str = vocabulary

    @logger.catch
    async def start(self) -> dict:
        if not self._tokens:
            tokens: List[str] = await self._read_files_start_text(settings.TOKENS_PATH_FILE)
            if not tokens:
                text = f'No tokens in file {settings.TOKENS_PATH_FILE}'
                logger.warning(text)
                return {'error': text}
            self._tokens = tokens
        try:
            self._proxy: str = await self._get_random_proxy()
        except ValueError as err:
            text = 'Прокси должна быть в формате user:password:ip_address:port'
            logger.exception(f"{text} {err}")
            return {'error': text}
        token: str = self._tokens.pop().strip()
        text_to_send: str = Vocabulary.get_message(file_name=self.vocabulary)
        if not text_to_send:
            text = f'Vocabulary error'
            logger.warning(text)
            return {'error': text}
        payload = {
            'token': token,
            'proxy': self._proxy,
            'channel': self.channel,
            'text_to_send': text_to_send
        }

        result: dict = await MessageSender(**payload).send_message_to_discord()
        logger.debug(f'Send result: {result}')
        result_data: dict = result.get('data', {})
        if result_data:
            return {'result': result_data}
        return {'error': result.get("message")}

    @staticmethod
    @logger.catch
    async def _read_files_start_text(file_name: str) -> List[str]:
        if not os.path.exists(file_name):
            logger.error(f'{file_name} file not found')
            return []
        with open(file_name, encoding="utf-8") as f:
            result: List[str] = f.readlines()
        return result

    @logger.catch
    async def _get_random_proxy(self) -> str:
        proxies: List[str] = await self._read_files_start_text(settings.PROXIES_PATH_FILE)
        random_proxy: str = random.choice(proxies)
        user, password, ip, port = random_proxy.strip().split(':')

        return f"http://{user}:{password}@{ip}:{port}/"


class Parser(GetRequest):

    def __init__(self, channel: int):
        super().__init__()
        self.channel: int = channel
        self.vocabulary: str = settings.PARSED_PATH_FILE
        self.token = settings.PARSING_TOKEN

    async def parse_data(self) -> dict:
        if not self.token:
            text = 'Не задан токен для парсинга PARSING_TOKEN в файле .env'
            logger.error(f"{text}")
            return {'error': text}
        limit: int = settings.MESSAGES_COUNT if 1 <= settings.MESSAGES_COUNT <= 100 else 100
        self.url = DISCORD_BASE_URL + f'{self.channel}/messages?limit={limit}'
        data: Dict[str, List[dict]] = await self.send_request()
        self._save_data(data)
        logger.debug(f"Parsed: {len(data)}")
        return {'result': len(data['data'])}

    def _save_data(self, data: Dict[str, List[dict]]):
        messages: List[dict] = data.get('data')
        results: List[str] = [f"{message['content']}\n" for message in messages if
                              message.get('content')]
        with open(self.vocabulary, 'a', encoding='utf-8') as f:
            f.writelines(results)


class MessageSender(PostRequest):
    """Отправляет сообщение в дискорд-канал"""

    def __init__(self, token: str, proxy: str, channel: int, text_to_send: str):
        super().__init__()
        self.token: str = token
        self.proxy: str = proxy
        self.channel: int = channel
        self._data_for_send: dict = {}
        self.text_to_send: str = text_to_send

    @logger.catch
    async def send_message_to_discord(self) -> dict:
        """Отправляет данные в канал дискорда, возвращает результат отправки."""

        text: str = (
            f"\nSend to channel: [{self.channel}]:"
            f"\tMessage text: [{self.text_to_send}]"
        )
        logger.debug(text)
        self._data_for_send = {
            "content": self.text_to_send,
            "tts": "false"
        }
        self.url = DISCORD_BASE_URL + f'{self.channel}/messages?'

        return await self.send_request()
