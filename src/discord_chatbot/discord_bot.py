import os.path
import random
from typing import List, Dict

from discord_chatbot.requesters import PostRequest, GetRequest
from discord_chatbot.config import logger, settings, DISCORD_BASE_URL

from discord_chatbot.vocabulary import Vocabulary, VocabularyException


class DiscordBot:
    """Send messages to channel from vocabulary

    Attributes
        channel: int
            Discord channel

        vocabulary: str
            Filename from which will be read messages for sending

    Methods
        start
    """

    def __init__(self, channel: int, vocabulary: str):
        self.channel: int = channel
        self.vocabulary: str = vocabulary
        self._tokens: List[str] = []
        self._proxy: List[str] = []

    @logger.catch
    async def start(self) -> dict:
        """
        Read tokens from settings.TOKENS_PATH_FILE
        Read proxies from settings.PROXIES_PATH_FILE and get random
        Read messages from vocabulary

        Send messages to channel using tokens and proxies"""

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
        try:
            text_to_send: str = Vocabulary.get_message(file_name=self.vocabulary)
        except VocabularyException as err:
            logger.error(f"Vocabulary ERROR: {err.text}")
            return {'error': err.text}
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

    @logger.catch
    async def _get_random_proxy(self) -> str:
        proxies: List[str] = await self._read_files_start_text(settings.PROXIES_PATH_FILE)
        random_proxy: str = random.choice(proxies)
        user, password, ip, port = random_proxy.strip().split(':')

        return f"http://{user}:{password}@{ip}:{port}/"

    @staticmethod
    @logger.catch
    async def _read_files_start_text(file_name: str) -> List[str]:
        if not os.path.exists(file_name):
            logger.error(f'{file_name} file not found')
            return []
        with open(file_name, encoding="utf-8") as f:
            result: List[str] = f.readlines()
        return result


class Parser(GetRequest):
    """Get messages from discord channel
    and saving to file them content

    Attributes
        channel: int
            Discord channel

        token: str = ''
            Discord token. By default loads from settings
        vocabulary: str = ''
            Filename in which will be saved content messages

    Methods
        parse_data

    """

    def __init__(self, channel: int, token: str = '', vocabulary: str = ''):
        super().__init__()
        self.channel: int = channel
        self.token = token or settings.PARSING_TOKEN
        self.vocabulary: str = vocabulary or settings.PARSED_PATH_FILE

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
    """Send message to discord channel

    Attributes
        token: str
            Discord token
        proxy: str
            Example: proxy = f"http://{user}:{password}@{ip}:{port}/"
        channel: int
            Discord channel

        text_to_send: str
            Text which will be sent

    Methods
        send_message_to_discord

    """

    def __init__(self, token: str, proxy: str, channel: int, text_to_send: str):
        super().__init__()
        self.token: str = token
        self.proxy: str = proxy
        self.channel: int = channel
        self._data_for_send: dict = {}
        self.text_to_send: str = text_to_send

    @logger.catch
    async def send_message_to_discord(self) -> dict:
        """Sends data to the discord channel, returns the result of sending"""

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
