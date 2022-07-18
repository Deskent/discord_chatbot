#!/usr/local/bin/python
# -*- coding: UTF-8 -*-
import os

from sys import platform


python: str = 'python3'
if platform == "win32":
    python: str = 'python'


command: str = (
    f'{python} -m pip install --upgrade pip && '
    f'{python} -m pip install --upgrade discord-chatbot-deskent'
)

print("Install dependents...")
status: int = os.system(command)
success: bool = status == 0

from discord_chatbot import start_bot


if __name__ == '__main__':
    if success:
        print("Install dependents... OK")
        start_bot()
