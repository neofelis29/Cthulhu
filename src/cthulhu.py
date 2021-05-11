from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
import time

import pandas as pd
from dotenv import load_dotenv
from pandas import DataFrame
from pip._vendor import requests

KRAKEN_API_KEY = os.getenv("KRAKEN_API_PRIVATE_KEY", default="")


class Cthulhu:

    def __init__(self):
        self.private_api_key = self._get_api_key()
        self.api_domain = "https://api.kraken.com"

    def _get_api_key(self):
        return KRAKEN_API_KEY

    def get_public_time(self):
        resp = requests.get('https://api.kraken.com/0/public/Time')
        print(resp.json())