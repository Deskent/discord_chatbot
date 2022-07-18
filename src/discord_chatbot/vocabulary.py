import os
import random
from typing import List

from discord_chatbot.config import logger, settings


class VocabularyException(Exception):
    def __init__(self, text: str = ''):
        self.text: str = text or 'Vocabulary error'

    def __str__(self):
        return self.text


class Vocabulary:
    """Reads file with text and returns 1 line

    Attributes
        file_name: str = ''
            By default: settings.VOCABULARY_PATH_FILE

    Methods
        get_message
    """

    __VOCABULARY: List[str] = []
    __PATH_TO_FILE: str = settings.VOCABULARY_PATH_FILE

    @classmethod
    @logger.catch
    def get_message(cls, file_name: str = '') -> str:
        """Returns a phrase from a list read from a file"""

        cls.__PATH_TO_FILE = file_name or settings.VOCABULARY_PATH_FILE
        vocabulary: list = cls.__get_vocabulary()
        if settings.PHRASE_RANDOM:
            random.shuffle(vocabulary)
        message_text: str = vocabulary.pop(0).strip()
        cls.__save_vocabulary(vocabulary)

        return message_text.lower()

    @classmethod
    @logger.catch
    def __get_vocabulary(cls) -> List[str]:
        if not cls.__VOCABULARY:
            cls.__read_vocabulary()

        return cls.__VOCABULARY

    @classmethod
    @logger.catch
    def __save_vocabulary(cls, vocabulary: List[str]):
        if not vocabulary:
            cls.__read_vocabulary()
        else:
            cls.__VOCABULARY = vocabulary

    @classmethod
    @logger.catch
    def __read_vocabulary(cls):
        if not os.path.exists(cls.__PATH_TO_FILE):
            raise VocabularyException(f"{cls.__PATH_TO_FILE} not found.")
        with open(cls.__PATH_TO_FILE, 'r', encoding='utf-8') as f:
            cls.__VOCABULARY: List[str] = f.readlines()
        if not cls.__VOCABULARY:
            raise VocabularyException(f'{cls.__PATH_TO_FILE} is empty.')
