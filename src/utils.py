import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.cbook as cbook
from datetime import datetime


def convert_timestamp_to_date(timestamp: int) -> datetime:
    return (datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'))

