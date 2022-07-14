import asyncio
import json
from abc import abstractmethod, ABC
from json import JSONDecodeError

import aiohttp
import aiohttp.client_exceptions
import aiohttp.http_exceptions

from discord_chatbot.config import logger


class RequestSender(ABC):
    """
    ABC class with errors hadling.

    Attributes
        url: str = ''

        token: str = ''

        _params: dict = {}

    """

    def __init__(self, url: str = ''):
        self.token: str = ''
        self.url: str = url
        self._params: dict = {}

    @abstractmethod
    async def _send(self, *args, **kwargs):
        pass

    async def send_request(self) -> dict:
        self._params: dict = {
            'url': self.url,
        }

        session_params: dict = {
            "trust_env": True,
            "connector": aiohttp.TCPConnector(),
        }
        answer: dict = {}
        try:

            async with aiohttp.ClientSession(**session_params) as session:
                if self.token:
                    session.headers['authorization']: str = self.token
                logger.debug(self._params)
                answer: dict = await self._send(session)
        except aiohttp.client_exceptions.ClientConnectorError as err:
            logger.error(f"aiohttp.client_exceptions.ClientConnectorError: {err}")
            answer.update(status=407, err=err)
        except aiohttp.http_exceptions.BadHttpMessage as err:
            logger.error(f"aiohttp.http_exceptions.BadHttpMessage: {err}")
            answer.update(status=407, err=err)
        except aiohttp.client_exceptions.ClientHttpProxyError as err:
            logger.error(f"aiohttp.client_exceptions.ClientHttpProxyError: {err}")
            answer.update(status=407, err=err)
        except asyncio.exceptions.TimeoutError as err:
            logger.error(f"asyncio.exceptions.TimeoutError: {err}")
            answer.update(status=-99, err=err)
        except aiohttp.client_exceptions.ClientOSError as err:
            logger.error(f"aiohttp.client_exceptions.ClientOSError: {err}")
            answer.update(status=-98, err=err)
        except aiohttp.client_exceptions.ServerDisconnectedError as err:
            logger.error(f"aiohttp.client_exceptions.ServerDisconnectedError: {err}")
            answer.update(status=-97, err=err)
        except aiohttp.client_exceptions.TooManyRedirects as err:
            logger.error(f"aiohttp.client_exceptions.TooManyRedirects: {err}")
            answer.update(status=-96, err=err)
        except aiohttp.client_exceptions.ContentTypeError as err:
            logger.error(f"aiohttp.client_exceptions.ContentTypeError: {err}")
            answer.update(status=-95, err=err)
        except Exception as err:
            text = f"Exception: {err}"
            answer.update(status=-100, err=err)
            logger.error(text)

        status = answer.get("status")
        logger.debug(f"Answer: {answer}")
        if status == 204:
            return dict(data={}, message='No content')
        elif status in range(400, 500):
            return dict(data={}, message=f'Error {status}')
        elif status not in range(200, 300):
            error_text: str = (
                f"\nStatus: {status}"
                f"\nUrl: {self.url}")
            logger.error(error_text)
        answer: dict = await self.__get_answer_data(answer)

        return {'data': answer.get("answer_data")}

    @logger.catch
    async def __get_answer_data(self, answer: dict) -> dict:
        """Parse data from answer

        :returns: Modified answer
        """

        answer_data: str = answer.get("answer_data")
        data = {}
        if not answer_data:
            answer.update(answer_data=data)

            return answer

        if isinstance(answer_data, str):
            try:
                data: dict = json.loads(answer_data)
            except JSONDecodeError as err:
                logger.error(
                    f"\nJSON ERROR: {err}"
                    f"\nAnswer data: {answer_data}"
                )
        elif isinstance(answer_data, (dict, list)):
            data = answer_data

        answer.update(answer_data=data)

        return answer


class GetRequest(RequestSender):
    """Класс для отправки GET запросов"""

    async def _send(self, session) -> dict:
        async with session.get(**self._params) as response:
            return {
                "status": response.status,
                "answer_data": await response.text()
            }


class PostRequest(RequestSender):

    def __init__(self):
        super().__init__()
        self._data_for_send: dict = {}
        self.proxy: str = ''

    async def _send(self, session) -> dict:
        """Отправляет данные в дискорд канал"""

        self._params.update(json=self._data_for_send)
        if self.proxy:
            self._params.update(proxy=self.proxy)
        async with session.post(**self._params) as response:
            return {
                "status": response.status,
                "answer_data": await response.json()
            }
