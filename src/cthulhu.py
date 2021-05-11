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
KRAKEN_DOMAIN = "https://api.kraken.com{}"
ASSETPAIRS = '/0/public/AssetPairs?pair={},{}'

logger = logging.getLogger(__name__)

class Cthulhu:

    def __init__(self):
        self.private_api_key = self._get_api_key()
        self.api_domain = KRAKEN_DOMAIN
        self.asset = self._get_asset()

    def _get_api_key(self):
        """
        Allows to get the api key in the environment variables
        :return:
        """
        return KRAKEN_API_KEY

    def _get_public_time(self) -> json:
        """
        Allows you to retrieve the current public time
        :return:
        """
        resp_time = requests.get(KRAKEN_DOMAIN.format('/0/public/Time'))
        return resp_time.json()

    def _get_system_status(self) -> json:
        """
        Allows you to retrieve information about the status of the API
        :return:
        """
        resp_status = requests.get(KRAKEN_DOMAIN.format('/0/public/SystemStatus'))
        return resp_status.json()

    def is_online(self) -> bool:
        """
        Returns True if the API is online, otherwise returns False
        :return:
        """
        resp_status = self._get_system_status().get("result").get("status")
        if resp_status == "online":
            return True
        else:
            return False

    def _get_asset(self) -> pd.DataFrame:
        """
        Allows you to retrieve information on assets
        :return:
        """
        resp_asset = requests.get(KRAKEN_DOMAIN.format('/0/public/Assets')).json()
        resp_asset_df = pd.DataFrame(resp_asset.get('result')).transpose()
        return resp_asset_df

    def get_tradable_asset(self, asset_one: str, asset_two: str) -> json:
        """

        """
        if self._is_asset(asset_one) and self._is_asset(asset_two):
            pair = ASSETPAIRS.format(asset_one, asset_one)
            resp_trade = requests.get(KRAKEN_DOMAIN.format(pair)).json()
            return resp_trade
        else:
            raise("Error: Asset name doesn't exist")


    def _is_asset(self, name_asset: str) -> bool:
        if name_asset in self.asset.altname.values:
            return True
        else:
            logger.warning("Asset {} don't exist".format(name_asset))
            return False
