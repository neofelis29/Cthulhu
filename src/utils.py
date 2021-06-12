import logging
from typing import List

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.cbook as cbook
from datetime import datetime
import pandas as pd


def convert_timestamp_to_date(timestamp: int) -> datetime:
    return (datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d:%H'))

def logger_init():
    # create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # create console handler which logs even debug messages
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)-7s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s')
    console_handler.setFormatter(formatter)
    # check if handlers are already present and if so, clear them before adding new handlers to avoid duplicate logs
    if (root_logger.hasHandlers()):
        root_logger.handlers.clear()
    root_logger.addHandler(console_handler)

def cast_to_kraken_list(list_of_elements: List[str]) -> str:
    """
    Cast into comma delimited list elements in string
    :param list_of_elements: List of the elements
    :return: Return a listt in string delimited with comma
    """
    list_kraken_format = ""
    for element in list_of_elements:
        list_kraken_format = list_kraken_format + element + ", "
    return list_kraken_format[:-2]
