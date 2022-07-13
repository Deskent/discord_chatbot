import os.path
import random
from typing import List

from config import settings, logger
from message_sender import MessageSender


class DiscordBot:
    def __init__(self):
        self.tokens: List[str] = []
        self.proxies: List[str] = []

    @staticmethod
    async def _read_files_start_text(file_name: str) -> List[str]:
        if not os.path.exists(file_name):
            logger.error(f'{file_name} file not found')
            return []
        with open(file_name, encoding="utf-8") as f:
            tokens: List[str] = f.readlines()
        return tokens

    async def start(self) -> dict:
        if not self.tokens:
            tokens: List[str] = await self._read_files_start_text(settings.TOKENS_PATH_FILE)
            if not tokens:
                text = 'No tokens in file'
                logger.warning(text)
                return {'error': text}
            self.tokens = tokens
        self.proxies = await self._read_files_start_text(settings.PROXIES_PATH_FILE)
        payload = {
            'token': self.tokens.pop().strip(),
            'proxy': random.choice(self.proxies).strip(),
            'channel': 932256559394861079
        }

        result: dict = await MessageSender(**payload).send_message_to_discord()
        logger.info(f'Send result: {result}')
        return {'result': result}
