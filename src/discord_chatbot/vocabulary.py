import os
import random

from discord_chatbot.config import logger, settings


class Vocabulary:
    """Reads file with text and returns 1 line"""

    __VOCABULARY: list = []
    __PATH_TO_FILE: str = settings.VOCABULARY_PATH_FILE

    @classmethod
    @logger.catch
    def get_message(cls, file_name: str = '') -> str:
        """Returns phrase from phrases list"""

        if file_name:
            cls.__PATH_TO_FILE = file_name
        try:
            vocabulary: list = cls.__get_vocabulary()
            if settings.PHRASE_RANDOM:
                random.shuffle(vocabulary)
            message_text: str = vocabulary.pop(0).strip()
            cls.__save_vocabulary(vocabulary)
        except (ValueError, TypeError, FileNotFoundError) as err:
            logger.error(f"Vocabulary ERROR: {err}")
            return ''
        return message_text.lower()

    @classmethod
    @logger.catch
    def __get_vocabulary(cls) -> list:
        if not cls.__VOCABULARY:
            cls.__read_vocabulary()

        return cls.__VOCABULARY

    @classmethod
    @logger.catch
    def __save_vocabulary(cls, vocabulary: list):
        if not isinstance(vocabulary, list):
            raise TypeError("TypeError: vocabulary is not list ")
        if not vocabulary:
            cls.__read_vocabulary()
        else:
            cls.__VOCABULARY = vocabulary

    @classmethod
    @logger.catch
    def __read_vocabulary(cls):
        if not os.path.exists(cls.__PATH_TO_FILE):
            raise FileNotFoundError(f"{cls.__PATH_TO_FILE} not found.")
        with open(cls.__PATH_TO_FILE, 'r', encoding='utf-8') as f:
            cls.__VOCABULARY: list = f.readlines()
            if not cls.__VOCABULARY:
                raise ValueError(f'{cls.__PATH_TO_FILE} is empty.')
