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

from src.asset import Asset

KRAKEN_API_KEY = os.getenv("KRAKEN_API_PRIVATE_KEY", default="")
KRAKEN_DOMAIN = "https://api.kraken.com{}"
ASSETPAIRS = "/0/public/AssetPairs?pair={}"
TICKER_INFORMATION = "/0/public/Ticker?pair={}"

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class AssetPair:

    def __init__(self, resp_asset: pd.Series):
        for key, value in resp_asset.to_dict().items():
            setattr(self, key, value)

    def get_information(self):
        """
        a
        Array of strings
        Ask [<price>, <whole lot volume>, <lot volume>]

        b
        Array of strings
        Bid [<price>, <whole lot volume>, <lot volume>]

        c
        Array of strings
        Last trade closed [<price>, <lot volume>]

        v
        Array of strings
        Volume [<today>, <last 24 hours>]

        p
        Array of strings
        Volume weighted average price [<today>, <last 24 hours>]

        t
        Array of integers
        Number of trades [<today>, <last 24 hours>]

        l
        Array of strings
        Low [<today>, <last 24 hours>]

        h
        Array of strings
        High [<today>, <last 24 hours>]

        o
        string
        Today's opening price
        :return:
        """
        ticker_information = TICKER_INFORMATION.format(self.altname)
        logger.info(TICKER_INFORMATION.format(KRAKEN_DOMAIN.format(ticker_information)))
        resp_ticker_inf = requests.get(KRAKEN_DOMAIN.format(ticker_information))
        return resp_ticker_inf.json()