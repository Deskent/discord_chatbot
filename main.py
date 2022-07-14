#!/usr/local/bin/python
# -*- coding: UTF-8 -*-
import subprocess

command = [
    'python3 -m pip install --upgrade pip && '
    'python3 -m pip install -r requirements.txt'
]
print("Install dependents...")
success = subprocess.run(command, stdout=subprocess.DEVNULL, shell=True)

from runner import start_bot

if success.returncode:
    exit(success.returncode)
start_bot()
