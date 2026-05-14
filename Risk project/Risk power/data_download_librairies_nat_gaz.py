import yfinance as yf
import pandas as pd
import numpy as np


def download_all_data(start_date, end_date):
    """
    Function to download data from Yahoo Finance
    """

    # Download data for the requested tickers
    tickers = ["NG=F"]
    data_download = yf.download(
        tickers=tickers,
        start=start_date,
        end=end_date,
        interval="1d",
        auto_adjust=False,
        progress=False,
        threads=False,
        group_by="column"
    )

    # Normalize: keep Adj Close or Close (closing prices(prix de cloture des marchés))
    if isinstance(data_download.columns, pd.MultiIndex):
        if 'Adj Close' in data_download.columns.get_level_values(0):
            data_download = data_download['Adj Close'].copy()
        elif 'Close' in data_download.columns.get_level_values(0):
            data_download = data_download['Close'].copy()

    # Show data
    print("✅ Data updated")
    print("📊 Available columns:", list(data_download.columns))
    print(data_download)

    # Percentage of missing values per column
    missing_pct = (data_download.isna().mean() * 100).round(2)
    print("\n📉 % of missing values per column:")
    print(missing_pct)

    # Check if all values of missing_pct are NaN
    if missing_pct.isnull().any() or (missing_pct == 100).all():
        print("❌ Error during download (all data missing)")
    else:
        print("Download finished")

    return data_download

