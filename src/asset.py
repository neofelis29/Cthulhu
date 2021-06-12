from __future__ import annotations

import pandas as pd
from pytrends.request import TrendReq
import warnings
import plotly.express as px

warnings.simplefilter("ignore", ResourceWarning)


class Asset:
    def __init__(self, asset_name: str, resp_asset: pd.Series):
        self.name = asset_name
        for key, value in resp_asset.to_dict().items():
            setattr(self, key, value)
        self.trend = TrendReq(hl='FR', tz=360)
        self.data = self._get_data_google_trend()

    def _get_data_google_trend(self) -> pd.DataFrame:
        """
        Allows you to retrieve the asset's google trend data for the month.
        :return:
        """
        self.trend.build_payload([self.altname], timeframe='today 1-m', geo='FR')
        trend = self.trend.interest_over_time()
        columns_name = trend.columns
        data = trend[columns_name[0]]
        data = data.resample('1H').interpolate('linear').to_frame().reset_index()
        data_asset = data[columns_name[0]]
        data_time = pd.to_datetime(data['date'], format='%Y-%m-%d %H:%M:%S')
        data = pd.concat([data_time, data_asset], axis=1)
        data = data.rename(columns={"date": "time"})
        data = data.set_index("time")
        return data

    def convert_time_stamp_to_date(self, data):
        data = data.reset_index(inplace=True)
        return data

    def graph_timestamp_trend(self):
        df = px.data.stocks(indexed=True) - 1
        fig = px.line(self.data[self.altname], title=self.name)
        fig.layout.template = 'plotly_dark'
        fig.show()
