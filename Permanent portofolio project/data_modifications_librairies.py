import yfinance as yf
import pandas as pd
import numpy as np
import data_download_script as data_dl

def get_economic_for_ratio_data(start_date, end_date, tickers):
    """
    Retrieve the requested columns from data_dl.data_download_global for the specified period.
    """

    # Check that all_data is loaded
    if data_dl.data_download_global is None:
        raise RuntimeError("❌ data is empty. Run data_download_script() first.")

    # Filter by period and columns
    data_for_ratio = data_dl.data_download_global.loc[start_date:end_date, tickers]

    # # Percentage of missing values per column
    # missing_pct = (data_for_ratio.isna().mean() * 100).round(2)
    # print("\n📉 % of missing values per column:")
    # print(missing_pct)

    # Remove NaN values to avoid errors
    return data_for_ratio.dropna()


def get_economic_cadran_data(economic_quadrant, start_date, end_date):
    """
    Extract from data_dl.data_download_global the series corresponding to the given economic quadrant over the specified period, and display the % of missing values per column.
    """

    # Check that all_data is loaded
    if data_dl.data_download_global is None:
        raise RuntimeError("❌ data is empty. Run data_download_script() first.")

    # Mapping cadrans → tickers
    quadrants_tickers = {
        "Quadrant 1: Inflationary Bust": ['GC=F', '^GSPC'],
        "Quadrant 2: Inflationary Boom": ['GC=F', '^GSPC'],
        "Quadrant 3: Deflationary Bust": ['^FVX', '^TYX', '^GSPC'],
        "Quadrant 4: Deflationary Boom": ['^FVX', '^TYX', '^GSPC'],
    }
    if economic_quadrant not in quadrants_tickers:
        raise ValueError(f"Error: Invalid quadrant ({economic_quadrant})")

    tickers = quadrants_tickers[economic_quadrant]

    # Filter by period and columns
    data_for_economic_cadrant = data_dl.data_download_global.loc[start_date:end_date, tickers]

    # # Percentage of missing values per column
    # missing_pct = (data_for_economic_cadrant.isna().mean() * 100).round(2)
    # print("\n📉 % of missing values per column:")
    # print(missing_pct)

    # Remove NaN values to avoid errors
    return  data_for_economic_cadrant.dropna()

