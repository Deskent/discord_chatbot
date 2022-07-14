import os
import random

from config import logger, settings


class Vocabulary:
    """Работает с файлом фраз для отправки в дискорд"""

    __VOCABULARY: list = []
    __PATH_TO_FILE: str = settings.VOCABULARY_PATH_FILE

    @classmethod
    @logger.catch
    def get_message(cls, file_name: str = '') -> str:
        """Returns random phrase from phrases list"""

        if file_name:
            cls.__PATH_TO_FILE = file_name
        vocabulary: list = cls.__get_vocabulary()
        try:
            random.shuffle(vocabulary)
            message_text: str = vocabulary.pop(0).strip()
            cls.__set_vocabulary(vocabulary)
        except (ValueError, TypeError, FileNotFoundError) as err:
            logger.error(f"Vocabulary ERROR: {err}")
            return ''
        else:
            length: int = len(message_text)
            if length > 60:
                return cls.get_message()
            return message_text.lower()

    @classmethod
    @logger.catch
    def __get_vocabulary(cls) -> list:
        if not cls.__VOCABULARY:
            cls.__update_vocabulary()

        return cls.__VOCABULARY

    @classmethod
    @logger.catch
    def __set_vocabulary(cls, vocabulary: list):
        if not isinstance(vocabulary, list):
            raise TypeError("TypeError: vocabulary is not list ")
        if not vocabulary:
            cls.__update_vocabulary()
        else:
            cls.__VOCABULARY = vocabulary

    @classmethod
    @logger.catch
    def __update_vocabulary(cls):
        if not os.path.exists(cls.__PATH_TO_FILE):
            raise FileNotFoundError(f"{cls.__PATH_TO_FILE} error: ")
        with open(cls.__PATH_TO_FILE, 'r', encoding='utf-8') as f:
            cls.__VOCABULARY = f.readlines()