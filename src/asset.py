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
from pytrends.request import TrendReq
import warnings
warnings.simplefilter("ignore", ResourceWarning)

class Asset:
    def __init__(self, asset_name: str, resp_asset: pd.Series):
        self.name = asset_name
        for key, value in resp_asset.to_dict().items():
            setattr(self, key, value)
        self.trend = TrendReq(hl='FR', tz=360)

    def get_data_google_trend(self) -> pd.DataFrame:
        """
        Allows you to retrieve the asset's google trend data for the month.
        :return:
        """
        self.trend.build_payload([self.name], timeframe='today 1-m', geo='FR')
        return self.trend.interest_over_time()


