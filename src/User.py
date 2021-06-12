import json
from typing import List
from src.cthulhu import Cthulhu
import pandas as pd

class User:
    def __init__(self, cthulhu: Cthulhu):
        self.cthulhu = cthulhu
        self.balance = cthulhu.get_balance()
        self.open_orders = cthulhu.get_open_orders()["result"]
        self.closed_orders = cthulhu.get_closed_orders()

    def get_open_orders(self):
        return pd.DataFrame(self.open_orders["open"]).transpose()

