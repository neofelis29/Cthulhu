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
from typing import List, Tuple

import pandas as pd
from dotenv import load_dotenv, find_dotenv
from pandas import DataFrame
from pip._vendor import requests

from src.asset import Asset
from src.pair_asset import AssetPair
from src.utils import cast_to_kraken_list
from src.type import Type
from src.order_type import Order_type

load_dotenv()

KRAKEN_API_PRIVATE_KEY = os.getenv("KRAKEN_API_PRIVATE_KEY", default="")
KRAKEN_API_KEY = os.getenv("KRAKEN_API_KEY", default="")

KRAKEN_URL = "https://api.kraken.com"
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
        resp_asset = requests.get(KRAKEN_DOMAIN.format('/0/public/Assets?assetVersion=2')).json()
        resp_asset_df = pd.DataFrame(resp_asset.get('result')).transpose()
        return resp_asset_df

    def get_asset(self, asset_name: str) -> Asset:
        """
        Retrieves information from an asset and returns an asset object
        :param asset_name: Code name of the asset
        :return: Asset object
        """
        if self._is_asset(asset_name):
            with open('../codes/asset_code.json') as json_file:
                codes_assets = json.load(json_file)
                asset = Asset(asset_name, self.assets.loc[codes_assets.get(asset_name)])
                return asset
        else:
            logger.warning("Asset {} don't exist".format(asset_name))
            raise Exception("ERROR: Asset don't exist")

    def _get_tradable_asset(self) -> pd.DataFrame:
        """
        Retrieves all available assets
        :return: Return a dataframe of all assets
        """
        resp_trbl_asset = requests.get(KRAKEN_DOMAIN.format('/0/public/AssetPairs?assetVersion=2')).json()
        return pd.DataFrame(resp_trbl_asset.get('result')).transpose()

    def get_pair_asset(self, asset_one: Asset, asset_two: Asset) -> AssetPair:
        """
        Convert asset name to version 0
        :param asset_two:
        :param asset_one:
        :return:
        """
        if self._is_pair_asset(asset_one, asset_two):
            pair_asset_name = "{}/{}".format(asset_one.altname, asset_two.altname)
            trdbl = self.tradable_asset.loc[(self.tradable_asset.wsname == pair_asset_name)]
            return AssetPair(asset_one, asset_two, trdbl.squeeze(axis=0))
        else:
            raise Exception ("Error: pair asset don't exist")

    def _is_pair_asset(self, asset_one: Asset, asset_two: Asset) -> bool:
        """
        Check if the pair asset exist
        :param asset_one: Asset object
        :param asset_two: Asset object
        :return: True if the pair asset exist
        """
        str_pair = "{}/{}".format(asset_one.altname, asset_two.altname)
        wsname = self.tradable_asset.wsname
        if str_pair in self.tradable_asset.wsname.values:
            return True
        else:
            return False

    def _is_asset(self, code_asset: str) -> bool:
        """
        Check that the asset exists
        :param name_asset: Name of the asset
        :return: Return true if the asset exist
        """
        with open('../codes/asset_code.json') as json_file:
            codes_assets = json.load(json_file)
            if code_asset in codes_assets:
                return True
            else:
                logger.warning("Asset {} don't exist".format(code_asset))
                return False

    def _get_signature(self, urlpath: str, data: json):
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

    def get_open_orders(self) -> json:
        """
        Retrieve information about the open order of the account
        :return: Json information about the open order
        """
        resp = self._request('/0/private/OpenOrders', {"nonce": str(int(1000 * time.time())), "trades": True})
        return resp

    def get_closed_orders(self) -> json:
        """
        Retrieve information about the closed order of the account
        :return: Json information about the closed order
        """
        resp = self._request('/0/private/ClosedOrders', {"nonce": str(int(1000 * time.time())), "userref": 36493663})
        return resp

    def get_information_orders(self, ids_list: List[str]) -> json:
        """
        Retrieve information about specific orders.
        :param ids: List of ids of the orders
        :return: Json informations about the specific orders
        """
        string_list_ids = cast_to_kraken_list(ids_list)
        resp = self._request('/0/private/QueryOrders', {
            "nonce": str(int(1000 * time.time())),
            "txid": string_list_ids,
            "trades": True})
        return resp

    def extract_asset_from_altname(self, altname: str) -> Tuple[str, str]:
        """
        Extract the name of asset from altname of pair of asset
        :param altname: altname of pair of asset
        :return: The name of the asset which compose the pair
        """
        if altname in self.tradable_asset.altname:
            name = self.tradable_asset.wsname.loc[self.tradable_asset.altname == altname].tolist()[0]
            asset_altname_list = name.split("/")
            asset_name_one = self.cast_asset_name_to_altname(asset_altname_list[0])
            asset_name_two = self.cast_asset_name_to_altname(asset_altname_list[1])
            return asset_name_one, asset_name_two

    def cast_asset_name_to_altname(self, asset_name):
        """
        Cast asset name to altname
        :param asset_name:
        :return: The altname of asset name
        """
        with open('../codes/asset_name.json') as json_file:
            codes_assets = json.load(json_file)
            if asset_name in codes_assets:
                return codes_assets[asset_name]

    def cancel_order(self, id: str) -> bool:
        """
        Cancel a particular open order
        :param id: Open order transaction ID
        :return: True if succeed
        """
        resp = self._request('/0/private/CancelOrder', {
            "nonce": str(int(1000 * time.time())),
            "txid": id
        })
        return True

    def add_order(self, volume: float, pair: str, price: float, order_type: Order_type, type: Type) -> bool:
        resp = self._request('/0/private/AddOrder', {
            "nonce": str(int(1000 * time.time())),
            "ordertype": order_type,
            "type": type,
            "volume": volume,
            "pair": pair,
            "price": price
        })
