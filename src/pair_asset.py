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
from src.utils import convert_timestamp_to_date

KRAKEN_API_KEY = os.getenv("KRAKEN_API_PRIVATE_KEY", default="")
KRAKEN_DOMAIN = "https://api.kraken.com{}"
ASSETPAIRS = "/0/public/AssetPairs?pair={}"
TICKER_INFORMATION = "/0/public/Ticker?pair={}"
OHLC="/0/public/OHLC?pair={}&interval={}"
TIME_INTERVAL = [1,5,15,30,60,240,1440,10080,21600]

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class AssetPair:

    def __init__(self, asset_one: Asset, asset_two: Asset, resp_asset: pd.Series):
        self.name = asset_one.altname+"/"+asset_two.altname
        resp_asset = resp_asset
        for key, value in resp_asset.to_dict().items():
            setattr(self, key, value)

    def get_ticker_information(self):
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
        logger.info(KRAKEN_DOMAIN.format(ticker_information))
        resp_ticker_inf = requests.get(KRAKEN_DOMAIN.format(ticker_information))
        resp_df = pd.DataFrame(resp_ticker_inf.json().get("result"))
        return resp_df

    def get_data(self, interval: int) -> pd.Dataframe:
        """
        interval should should be one of this: 1 5 15 30 60 240 1440 10080 21600
        :param interval: Enum(1 5 15 30 60 240 1440 10080 21600)
        :return:
        """
        if interval in TIME_INTERVAL:
            ohlc = OHLC.format(self.altname, interval)
            logger.info("Request: {}".format(KRAKEN_DOMAIN.format(ohlc, interval)))
            resp_status = requests.get(KRAKEN_DOMAIN.format(ohlc)).json()
            del resp_status["result"]["last"]
            data = pd.DataFrame.from_dict(resp_status["result"])
            column_name = data.columns[0]
            data = pd.DataFrame(data[column_name].tolist(), columns=['time', 'open', 'high', 'low', 'close', 'vwap', 'volume', 'count'])
            data.time = data.apply(lambda x: convert_timestamp_to_date(x.time), axis=1)
            data = data.set_index("time")
            data = data.astype(float)
            return data
        else:
            return ""
