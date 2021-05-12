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

class Asset:

    def __init__(self, asset_name: str, resp_asset: pd.Series):
        self.name = asset_name
        for key, value in resp_asset.to_dict().items():
            setattr(self, key, value)


