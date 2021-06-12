from __future__ import annotations

import itertools
import logging
import os
from datetime import datetime
from typing import Tuple, List

import plotly.graph_objects as go
from fbprophet import Prophet
from fbprophet.diagnostics import cross_validation, performance_metrics
from pip._vendor import requests
from src.asset import Asset
import pandas as pd
import numpy as np

KRAKEN_API_KEY = os.getenv("KRAKEN_API_PRIVATE_KEY", default="")
KRAKEN_DOMAIN = "https://api.kraken.com{}"
ASSETPAIRS = "/0/public/AssetPairs?pair={}"
TICKER_INFORMATION = "/0/public/Ticker?pair={}"
OHLC = "/0/public/OHLC?pair={}&interval={}"
TIME_INTERVAL = [1, 5, 15, 30, 60, 240, 1440, 10080, 21600]
INTERVAL = 60
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class AssetPair:

    def __init__(self, asset_one: Asset, asset_two: Asset, resp_asset: pd.Series):
        self.name = asset_one.altname + "/" + asset_two.altname
        resp_asset = resp_asset
        for key, value in resp_asset.to_dict().items():
            setattr(self, key, value)
        self.ticker_information = self._get_ticker_information()

        self.data = self._get_data()
        self.asset_one = asset_one
        self.asset_two = asset_two

    def _get_ticker_information(self):
        """
        Get information about the pair of asset
        :return: The information of the pair of asset
        """
        ticker_information = TICKER_INFORMATION.format(self.altname)
        logger.info(KRAKEN_DOMAIN.format(ticker_information))
        resp_ticker_inf = requests.get(KRAKEN_DOMAIN.format(ticker_information))
        resp_df = pd.DataFrame(resp_ticker_inf.json().get("result"))
        return resp_df

    def _get_data(self) -> pd.Dataframe:
        """
        interval should should be one of this: 1 5 15 30 60 240 1440 10080 21600
        :return:
        """
        if INTERVAL in TIME_INTERVAL:
            ohlc = OHLC.format(self.altname, INTERVAL)
            logger.info("Request: {}".format(KRAKEN_DOMAIN.format(ohlc, INTERVAL)))
            resp_status = requests.get(KRAKEN_DOMAIN.format(ohlc)).json()
            del resp_status["result"]["last"]
            data = pd.DataFrame.from_dict(resp_status["result"])
            column_name = data.columns[0]
            data = pd.DataFrame(data[column_name].tolist(),
                                columns=['time', 'open', 'high', 'low', 'close', 'vwap', 'volume', 'count'])
            data.time = data.apply(lambda x: datetime.fromtimestamp(x.time), axis=1)
            data = data.set_index("time")
            data = data.astype(float)
            return data
        else:
            return ""

    def compute_forecasting_prediction_graphic(self, input_data_model: pd.Dataframe, forecast: pd.Dataframe,
                                               forecasting_time: int) -> bool:
        """
        Create the plot from the forecasting prediction computed by the Prophet model
        :param input_data_model:
        :param forecast:
        :param forecasting_time:
        """
        left_limit = forecast.iloc[len(forecast) - forecasting_time]["ds"]
        right_limit = forecast.iloc[len(forecast) - 1]["ds"]
        df_model = input_data_model.set_index("ds")
        forecast = forecast.set_index("ds")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=forecast.index, y=forecast["yhat"],
                                 mode='lines+markers',
                                 name='forecast trend prediction for {} hours of {}'.format(forecasting_time,
                                                                                            self.name)))
        fig.add_trace(go.Scatter(x=df_model.index, y=df_model["y"],
                                 mode='lines+markers',
                                 name='real trend: {}'.format(self.name)))
        fig.add_vrect(x0=left_limit, x1=right_limit, line_width=0, fillcolor="red", opacity=0.2)
        fig.update_xaxes(nticks=35)
        fig.layout.template = 'plotly_dark'
        fig.show()
        return True

    def cast_to_prophet_data(self):
        """
        Cast the dataframe if crypto data into a dataframe that can be handle by Prophet model
        :return:
        """
        data_index_reset = self.data.reset_index()
        input_data_model = data_index_reset.rename(columns={'time': 'ds', 'open': 'y'})
        return input_data_model

    def _check_optional_input_data_list(self, optional_input_data_list: List[str]) -> bool:
        if optional_input_data_list is None:
            return False
        for optional_input_data in optional_input_data_list:
            if optional_input_data not in self.data.columns:
                logger.warning("optional data given doesn't exist in the input data model")
                return False
        return True

    def predict_crypto_currency(self, optional_input_data_list: List[str] = None, graph: bool = False,
                                forecasting_time: int = 24 * 2) -> pd.Tuple[bool, pd.Dataframe]:
        """
        Compute prediction with the current information of the pair of asset with Prophet model
        :param optional_input_data_list: List of the optional data to give to the Prophet model
        :param graph: If graph is True the plot is computed otherwise not
        :param forecasting_time: The time in hours we want to predict
        :return: The prediction of the crypto currency
        """
        prophet_model = Prophet(changepoint_prior_scale=0.01, seasonality_prior_scale=0.1, growth="linear")
        input_data_model = self.cast_to_prophet_data()
        if self._check_optional_input_data_list(optional_input_data_list):
            for optional_input_data in optional_input_data_list:
                prophet_model.add_regressor(optional_input_data, standardize=False)

        prophet_model.fit(input_data_model)
        future = prophet_model.make_future_dataframe(periods=forecasting_time, freq='H')
        forecast = prophet_model.predict(df=future)
        if graph:
            logger.info("Graphic computing")
            self.compute_forecasting_prediction_graphic(input_data_model, forecast, forecasting_time)
        return True, forecast

    def predict_crypto_currency_optimized(self, optional_input_data_list: List[str] = None, graph: bool = False,
                                          forecasting_time: int = 24 * 2) -> Tuple[bool, pd.Dataframe]:
        """

        :param forecasting_time: Time to predict in hours
        """
        best_params = self.find_best_params_prophet_model()
        prophet_model = Prophet(changepoint_prior_scale=best_params["changepoint_prior_scale"], seasonality_prior_scale=best_params["seasonality_prior_scale"])
        input_data_model = self.cast_to_prophet_data()
        if self._check_optional_input_data_list(optional_input_data_list):
            for optional_input_data in optional_input_data_list:
                prophet_model.add_regressor(optional_input_data, standardize=False)

        prophet_model.fit(input_data_model)
        future = prophet_model.make_future_dataframe(periods=forecasting_time, freq='H')
        forecast = prophet_model.predict(df=future)
        if graph:
            self.compute_forecasting_prediction_graphic(input_data_model, forecast, forecasting_time)

    def find_best_params_prophet_model(self) -> dict:
        """
        Grid search to find the best paramter that minimize the RMSE value
        :return: A dict that contain the best parameters for the Prophet model
        """
        input_data_model = self.cast_to_prophet_data()

        param_grid = {
            'changepoint_prior_scale': [0.001, 0.01, 0.1, 0.5],
            'seasonality_prior_scale': [0.01, 0.1, 1.0, 10.0],
        }

        # Generate all combinations of parameters
        all_params = [dict(zip(param_grid.keys(), v)) for v in itertools.product(*param_grid.values())]
        rmses = []  # Store the RMSEs for each params here
        # Use cross validation to evaluate all parameters
        for params in all_params:
            m = Prophet(**params)
            # Fit model with given m.add_regressor('add1')
            m.add_regressor('close')
            m.fit(input_data_model)

            df_cv = cross_validation(m, horizon='2 days', parallel="processes")
            df_p = performance_metrics(df_cv, rolling_window=1)
            rmses.append(df_p['rmse'].values[0])
        # Find the best parameters
        tuning_results = pd.DataFrame(all_params)
        tuning_results['rmse'] = rmses
        best_params = all_params[np.argmin(rmses)]
        return best_params
