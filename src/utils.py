import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.cbook as cbook
from datetime import datetime
import pandas as pd


def convert_timestamp_to_date(timestamp: int) -> datetime:
    return (datetime.utcfromtimestamp(timestamp).strftime('%d %H:%M'))

def graph_timestamp(data: pd.Series, title: str=""):
    plt.style.use('dark_background')
    # Create figure and plot space
    fig, ax = plt.subplots(figsize=(10, 6))

    # Add x-axis and y-axis
    ax.plot(data.index.values,
            data.values)

    # Set title and labels for axes
    ax.set(xlabel="Date",
           ylabel="Value",
           title=title)
    ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=30000))
    ax.legend(data.columns.tolist())
    plt.setp(ax.get_xticklabels(), rotation=45)
    plt.grid(linestyle='dotted')
    plt.show()