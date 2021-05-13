from __future__ import annotations

import base64
import hashlib
import hmac
import json
import logging
import os
import subprocess
import sys
import time
import urllib

import pandas as pd
from dotenv import load_dotenv, find_dotenv
from pandas import DataFrame
from pip._vendor import requests

from src.asset import Asset
from src.pair_asset import AssetPair

load_dotenv()

KRAKEN_API_PRIVATE_KEY = os.getenv("KRAKEN_API_PRIVATE_KEY", default="")
KRAKEN_API_KEY = os.getenv("KRAKEN_API_KEY", default="")

KRAKEN_URL =  "https://api.kraken.com"
KRAKEN_DOMAIN = "https://api.kraken.com{}"
TICKER_INFORMATION = "Ticker?pair={}"
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Cthulhu:

    def __init__(self):
        self.private_api_key = self._get_api_key()
        self.api_domain = KRAKEN_DOMAIN
        self.assets = self._get_assets()
        self.tradable_asset = self._get_tradable_asset()

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

    def _get_assets(self) -> pd.DataFrame:
        """
        Allows you to retrieve information on assets
        :return:
        """
        resp_asset = requests.get(KRAKEN_DOMAIN.format('/0/public/Assets?assetVersion=1')).json()
        resp_asset_df = pd.DataFrame(resp_asset.get('result')).transpose()
        return resp_asset_df

    def get_asset(self, asset_name: str) -> Asset:
        """
        Retrieves information from an asset and returns an asset object
        :param asset_name: Name of the asset
        :return: Asset object
        """
        if self._is_asset(asset_name):
            asset = Asset(asset_name, self.assets.loc[asset_name])
            return asset
        else:
            logger.warning("Asset {} don't exist".format(asset_name))
            raise Exception("ERROR: Asset don't exist")

    def _get_tradable_asset(self) -> pd.DataFrame:
        """
        Retrieves all available assets
        :return: Return a dataframe of all assets
        """
        resp_trbl_asset = requests.get(KRAKEN_DOMAIN.format('/0/public/AssetPairs?assetVersion=1')).json()
        return pd.DataFrame(resp_trbl_asset.get('result')).transpose()

    def get_pair_asset(self, asset_one: Asset, asset_two: Asset) -> AssetPair:
        """
        Convert asset name to version 0
        :param asset_two:
        :param asset_one:
        :return:
        """
        if self._is_pair_asset(asset_one, asset_two):
            pair_asset_name = "{}/{}".format(asset_one.name, asset_two.name)
            trbl = self.tradable_asset.loc[pair_asset_name]
            return AssetPair(pair_asset_name, trbl)
        else:
            raise BaseException ("Error: pair asset don't exist")

    def _is_pair_asset(self, asset_one: Asset, asset_two: Asset) -> bool:
        """
        Check if the pair asset exist
        :param asset_one: Asset object
        :param asset_two: Asset object
        :return: True if the pair asset exist
        """
        str_pair = "{}/{}".format(asset_one.name, asset_two.name)
        if str_pair in self.tradable_asset.index:
            return True
        else:
            return False

    def _is_asset(self, name_asset: str) -> bool:
        """
        Check that the asset exists
        :param name_asset: Name of the asset
        :return: Return true if the asset exist
        """
        if name_asset in self.assets.altname.index:
            return True
        else:
            logger.warning("Asset {} don't exist".format(name_asset))
            return False

    def _get_signature(self,urlpath: str, data: json):
        """
        Create the signature to connect to the Kraken API
        :param urlpath: Url which be given in post method
        :param data: Data to send with in the url
        :return:
        """
        postdata = urllib.parse.urlencode(data)
        encoded = (str(data['nonce']) + postdata).encode()
        message = urlpath.encode() + hashlib.sha256(encoded).digest()

        mac = hmac.new(base64.b64decode(KRAKEN_API_PRIVATE_KEY), message, hashlib.sha512)
        sigdigest = base64.b64encode(mac.digest())
        return sigdigest.decode()

    def _request(self, uri_path: str, data: json) -> json:
        """
        Attaches auth headers and returns results of a POST request
        :param uri_path:
        :param data:
        :return:
        """
        headers = {}
        headers['API-Key'] = KRAKEN_API_KEY
        # get_kraken_signature() as defined in the 'Authentication' section
        headers['API-Sign'] = self._get_signature(uri_path, data)
        req = requests.post((KRAKEN_DOMAIN.format(uri_path)), headers=headers, data=data)
        return req.json()

    def get_balance(self) -> json:
        """
        Allows you to retrieve information about the balance of the various assets in your account
        :return: Json information about balanceS
        """
        resp = self._request('/0/private/Balance', {"nonce": str(int(1000 * time.time()))})
        return resp

