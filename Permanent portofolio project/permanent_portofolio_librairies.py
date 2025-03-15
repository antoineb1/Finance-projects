import yfinance as yf
import pandas as pd
import numpy as np
import requests

# Fetching data on gold, bond yields, and stocks
def get_economic_for_ratio_data(start_date, end_date):
    selected_tickers = ['GC=F', '^GSPC', '^FVX', '^TYX']
    dataframes = []
    for ticker in selected_tickers:
        try:
            df_var = yf.download(ticker, start=start_date, end=end_date, interval='1d', auto_adjust=False, progress=True)
            if 'Adj Close' in df_var.columns:
                df_var = df_var[['Adj Close']]
                df_var.rename(columns={'Adj Close': ticker}, inplace=True)
                dataframes.append(df_var)
        except Exception as e:
            print(f"Failed to download data for {ticker}: {e}")

    if not dataframes:
        raise ValueError("No data downloaded. Check the tickers and your internet connection.")

    data = pd.concat(dataframes, axis=1)
    print('\n\n')

    # Print missing data
    missing_data = data.isnull().mean() * 100
    print("⚠️ Warning: Some data is missing. Here is the percentage of null values per ticker:")
    print(missing_data)
    print('\n\n')

    return data.dropna()

# Determining inflation and growth ratios
def get_market_ratios(start_date, end_date):

    data = get_economic_for_ratio_data(start_date, end_date)

    # Ensuring that the tickers exist in the dataset
    required_tickers = ['GC=F', '^GSPC', '^FVX', '^TYX']
    for ticker in required_tickers:
        if ticker not in data.columns:
            raise KeyError(f"Ticker {ticker} is missing from the downloaded data.")

    # Calculation range
    data_size = data['GC=F'].size
    num_days = (pd.to_datetime(end_date) - pd.to_datetime(start_date)).days

    # Calculating the average bond yield over the period
    bond_avg = ((data['^FVX'].astype(float).squeeze() + data['^TYX'].astype(float).squeeze()) / 2) / 100
    data['Bond_Mean'] = bond_avg.rolling(window=data_size).mean()

    # Calculating growth over the period
    gold_growth = data['GC=F'].pct_change(periods=(data_size-1)).dropna().squeeze()
    equity_growth = data['^GSPC'].pct_change(periods=(data_size-1)).dropna().squeeze()

    # Selecting the last value as a scalar
    last_gold_growth = gold_growth
    last_bonds_mean = data['Bond_Mean'].dropna().iloc[-1] if not data['Bond_Mean'].dropna().empty else np.nan
    last_equity_growth = equity_growth

    # Calculating the daily interest rate with compounding
    annual_interest_rate = last_bonds_mean / 100
    daily_interest_rate = (1 + annual_interest_rate) ** (1 / 365) - 1
    last_bonds_growth = ((1 + daily_interest_rate) ** num_days - 1)*100

    print(f"📊 Last gold growth (US Dollar) over {num_days} days: {last_gold_growth*100:.2f}%")
    print(f"📈 Last growth of IWLE.DE (MSCI World in US Dollar) over {num_days} days: {last_equity_growth*100:.2f}%")
    print(f"💰 Average US bond yields (US Dollar) (average of 5-year and 15-year rates) over {num_days} days: {last_bonds_mean*100:.2f}%")
    print(f"📉 Last bond growth (average of 5-year and 15-year US rates) over {num_days} days: {last_bonds_growth*100:.2f}%")
    print('\n\n')

    # Ensuring values are not NaN
    if np.isnan(last_gold_growth) or np.isnan(last_bonds_growth) or np.isnan(last_equity_growth):
        raise ValueError("Unable to calculate growth ratios due to missing data.")

    # Calculating growth ratios
    gold_bonds_ratio = float(last_gold_growth / last_bonds_growth) if last_bonds_mean != 0 else np.nan
    gold_equity_ratio = float(last_gold_growth / last_equity_growth) if last_gold_growth != 0 else np.nan

    # Adjusting negative ratios to avoid sign errors
    if last_gold_growth < 0 and last_bonds_growth > 0 :
        gold_bonds_ratio = 0
    if last_gold_growth < 0 and last_equity_growth > 0 :
        gold_equity_ratio = 0

    print(f"ratio growth gold/bonds : {gold_bonds_ratio}")
    print(f"ratio growth gold/equity : {gold_equity_ratio}")
    print('\n\n')

    return gold_bonds_ratio, gold_equity_ratio

# Determining the economic quadrant
def determine_quadrant(gold_bonds_ratio, gold_equity_ratio):

    if gold_bonds_ratio > 2 and gold_equity_ratio > 2:
        return "Quadrant 1: Inflationary Bust"
    elif gold_bonds_ratio > 2 and gold_equity_ratio < 2:
        return "Quadrant 2: Inflationary Boom"
    elif gold_bonds_ratio < 0.5 and gold_equity_ratio > 2:
        return "Quadrant 3: Deflationary Bust"
    elif gold_bonds_ratio < 0.5 and gold_equity_ratio < 2:
        return "Quadrant 4: Deflationary Boom"
    else :
        return "Quadrant 5: Transition Quadrant"

# Fetching economic and financial data for the selected quadrant
def get_economic_cadran_data(economic_quadrant,start_date,end_date):

    # Dictionary of assets by quadrant
    quadrants_tickers = {
        "Quadrant 1: Inflationary Bust": ['GC=F', '^GSPC', '^FVX', '^TYX'],
        "Quadrant 2: Inflationary Boom": ['GC=F', '^GSPC', '^FVX', '^TYX'],
        "Quadrant 3: Deflationary Bust": ['ZN=F', '^GSPC'],
        "Quadrant 4: Deflationary Boom": ['ZN=F', '^GSPC']
    }

    # Checking if the selected quadrant is valid
    if economic_quadrant not in quadrants_tickers:
        raise ValueError(f"Error: Invalid quadrant ({economic_quadrant})")

    selected_tickers = quadrants_tickers[economic_quadrant]
    print(f"\n\n📊 Fetching data for {economic_quadrant}: {selected_tickers}\n\n")

    dataframes = []
    for ticker in selected_tickers:
        try:
            df_var = yf.download(ticker, start=start_date, end=end_date, interval='1d', auto_adjust=False, progress=True)
            if 'Adj Close' in df_var.columns:
                df_var = df_var[['Adj Close']]
                df_var.rename(columns={'Adj Close': ticker}, inplace=True)
                dataframes.append(df_var)
        except Exception as e:
            print(f"Failed to download data for {ticker}: {e}")

    if not dataframes:
        raise ValueError("No data downloaded. Check the tickers and your internet connection.")

    data = pd.concat(dataframes, axis=1)

    if data.isnull().values.any():
        missing_data = data.isnull().mean() * 100
        print('\n\n')
        print("⚠️ Warning: Some data is missing. Here is the percentage of null values per ticker:")
        print(missing_data)
        print('\n\n')

    return data.dropna()

# Determining the portfolio components
def get_final_portfolio(economic_quadrant,start_date, end_date):

    data = get_economic_cadran_data(economic_quadrant,start_date, end_date)

    # Dictionary of assets by quadrant
    quadrants_tickers = {
        "Quadrant 1: Inflationary Bust": ['GC=F', '^GSPC', '^FVX', '^TYX'],
        "Quadrant 2: Inflationary Boom": ['GC=F', '^GSPC', '^FVX', '^TYX'],
        "Quadrant 3: Deflationary Bust": ['ZN=F', '^GSPC'],
        "Quadrant 4: Deflationary Boom": ['ZN=F', '^GSPC']
    }

    if economic_quadrant not in quadrants_tickers:
        raise ValueError(f"Error: Invalid quadrant ({economic_quadrant})")

    required_tickers = quadrants_tickers[economic_quadrant]
    for ticker in required_tickers:
        if ticker not in data.columns:
            raise KeyError(f"Ticker {ticker} is missing from the downloaded data.")

    # Calculation of data size and number of days
    data_size = len(data)
    nb_days = (pd.to_datetime(end_date) - pd.to_datetime(start_date)).days

    # Risk-free investment rate
    last_bonds_growth = 0

    # Adjust bond data if the column contains '^FVX' or '^TYX'
    if '^FVX' in data.columns and '^TYX' in data.columns:
        bond_avg = ((data['^FVX'].astype(float).squeeze() + data['^TYX'].astype(float).squeeze()) / 2) / 100
        data['Bond_Mean'] = bond_avg.rolling(window=data_size).mean()

        # Calculation of daily interest rate with capitalization
        last_bonds_mean = data['Bond_Mean'].dropna().iloc[-1] if not data['Bond_Mean'].dropna().empty else np.nan
        if not np.isnan(last_bonds_mean):
            annual_interest_rate = last_bonds_mean / 100
            daily_interest_rate = (1 + annual_interest_rate) ** (1 / 365) - 1

            # Calculation of bond growth (in percentage) over the period
            last_bonds_growth = ((1 + daily_interest_rate) ** nb_days - 1) * 100

            # Replace all 'Bond_Mean' rows with 1 except the last one, which becomes last_bonds_growth
            data['Bond_Mean'] = 1
            data['Bond_Mean'] = data['Bond_Mean'].astype(float)
            data.loc[data.index[-1], 'Bond_Mean'] = 0 * (last_bonds_growth + 1)

        else:
            print("Error: Unable to calculate last_bonds_growth, Bond_Mean is NaN.")
            return None

        # Delete the columns '^FVX' '^TYX' 'Bond_Mean' from 'data'
        data = data.sort_index(axis=1)  # Sort column index
        data = data.drop(columns=['^FVX', '^TYX', 'Bond_Mean'])

    # Risk-free return
    returns_without_risk = last_bonds_growth

    # Calculation of daily returns
    returns = data.pct_change(periods=(data_size - 1)).dropna().squeeze()

    # Calculation of Sharpe ratio
    sharpe_ratios = (returns - returns_without_risk) / returns.std()

    # Remove negative weights (avoid short-selling)
    portfolio_weights = sharpe_ratios.clip(lower=0)

    # Check that there is at least one asset with a positive Sharpe ratio
    if portfolio_weights.sum() == 0:
        raise ValueError("All assets have negative Sharpe ratios, portfolio allocation is impossible.")

    # Re-normalization of weights to use 100% of capital
    portfolio_weights = portfolio_weights / portfolio_weights.sum()

    print("\n📊 Optimal portfolio allocation based on the Sharpe ratio (without short-selling):")
    print(portfolio_weights)

    return portfolio_weights