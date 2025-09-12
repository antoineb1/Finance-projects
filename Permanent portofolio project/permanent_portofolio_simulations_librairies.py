import yfinance as yf
import pandas as pd
import numpy as np
import data_modifications_librairies as data_modif

# Determining inflation and growth ratios
def get_market_ratios(start_date, end_date):

    # Required tickers
    required_tickers = ['GC=F', '^GSPC', '^FVX', '^TYX']

    # Initialize the dataset with a wider date range to avoid boundary errors
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    start_date_large = start - pd.Timedelta(days=15)
    end_date_large = end + pd.Timedelta(days=15)
    data = data_modif.get_economic_for_ratio_data(start_date_large, end_date_large,required_tickers)
    full_idx = pd.date_range(start_date_large, end_date_large, freq="D")
    data = data.reindex(full_idx).ffill()

    # Ensuring that the tickers exist in the dataset
    for ticker in required_tickers:
        if ticker not in data.columns:
            raise KeyError(f"Ticker {ticker} is missing from the downloaded data.")

    # Calculating the average bond yield over the period
    bond_avg = ((data['^FVX'].loc[start_date:end_date].dropna().astype(float).squeeze() + data['^TYX'].loc[start_date:end_date].dropna().astype(float).squeeze()) / 2) / 100
    data_size = len(bond_avg)
    data['Bond_Mean'] = bond_avg.rolling(window=data_size).mean()

    # Calculating growth (gold and equity) over the period
    gold_data = data['GC=F'].loc[start_date:end_date].dropna()
    gold_growth = (gold_data.iloc[-1] - gold_data.iloc[0]) / gold_data.iloc[0]
    equity_data = data['^GSPC'].loc[start_date:end_date].dropna()
    equity_growth = ((equity_data.iloc[-1] - equity_data.iloc[0]) / equity_data.iloc[0])

    # Selecting the last value as a scalar
    last_gold_growth = gold_growth
    last_bonds_mean = data['Bond_Mean'].dropna().iloc[-1] if not data['Bond_Mean'].dropna().empty else np.nan
    last_equity_growth = equity_growth

    # Calculation number of days
    num_days = (pd.to_datetime(end_date) - pd.to_datetime(start_date)).days

    # Calculating the daily interest rate with compounding
    annual_interest_rate = last_bonds_mean / 100
    daily_interest_rate = (1 + annual_interest_rate) ** (1 / 365) - 1
    last_bonds_growth = ((1 + daily_interest_rate) ** num_days - 1)*100

    # print(f"📊 Last gold growth (US Dollar) over {num_days} days: {last_gold_growth*100:.2f}%")
    # print(f"📈 Last growth of IWLE.DE (MSCI World in US Dollar) over {num_days} days: {last_equity_growth*100:.2f}%")
    # print(f"💰 Average US bond yields (US Dollar) (average of 5-year and 15-year rates) over {num_days} days: {last_bonds_mean*100:.2f}%")
    # print(f"📉 Last bond growth (average of 5-year and 15-year US rates) over {num_days} days: {last_bonds_growth*100:.2f}%")
    # print('\n\n')

    # Ensuring values are not NaN
    if np.isnan(last_gold_growth) or np.isnan(last_bonds_growth) or np.isnan(last_equity_growth):
        raise ValueError("Unable to calculate growth ratios due to missing data.")

    # Calculating growth ratios (change with the strategy)
    #gold_bonds_ratio = float(last_gold_growth / last_bonds_growth) if last_bonds_mean != 0 else np.nan
    gold_bonds_ratio = float(last_gold_growth)-0.05
    gold_equity_ratio = float(last_gold_growth - last_equity_growth)

    # Adjusting negative ratios to avoid sign errors
    # if last_gold_growth < 0 and last_bonds_growth > 0 :
    #     gold_bonds_ratio = 0
    # if last_gold_growth < 0 and last_equity_growth > 0 :
    #     gold_equity_ratio = 0

    # print(f"ratio growth gold/bonds : {gold_bonds_ratio}")
    # print(f"ratio growth gold/equity : {gold_equity_ratio}")
    # print('\n\n')

    return gold_bonds_ratio, gold_equity_ratio


# Determining the economic quadrant
def determine_quadrant(gold_bonds_ratio, gold_equity_ratio):

    if gold_bonds_ratio > 0 and gold_equity_ratio > 5:
        return "Quadrant 1: Inflationary Bust"
    elif gold_bonds_ratio > 0 and gold_equity_ratio < 5:
        return "Quadrant 2: Inflationary Boom"
    elif gold_bonds_ratio < 0 and gold_equity_ratio > 5:
        return "Quadrant 3: Deflationary Bust"
    elif gold_bonds_ratio < 0 and gold_equity_ratio < 5:
        return "Quadrant 4: Deflationary Boom"
    else :
        return "Quadrant 5: Transition Quadrant"


# determine the return of the strategy
def get_return_of_investments(money,rebalance_days,economic_quadrant,start_date,end_date):

    # Dictionary of assets by quadrant
    quadrants_tickers = {
        "Quadrant 1: Inflationary Bust": ['GC=F', '^GSPC'],
        "Quadrant 2: Inflationary Boom": ['GC=F', '^GSPC'],
        "Quadrant 3: Deflationary Bust": ['^FVX', '^TYX', '^GSPC'],
        "Quadrant 4: Deflationary Boom": ['^FVX', '^TYX', '^GSPC'],
    }

    # Check the economic_quadrant
    if economic_quadrant not in quadrants_tickers:
        raise ValueError(f"Error: Invalid quadrant ({economic_quadrant})")

    # Init required tickers
    required_tickers = quadrants_tickers[economic_quadrant]

    # Convert input dates to datetime objects
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)

    # Compute the total number of days in the period
    nb_days = (end - start).days

    # Check rebalance_days
    if rebalance_days < 1:
        raise ValueError("rebalance_days must be >= 1")

    # Create the rebalancing dates based on the chosen frequency
    rebal_dates = list(pd.date_range(start=start, end=end, freq=f"{rebalance_days}D"))

    # Ensure the start date is included
    if rebal_dates[0] != start:
        rebal_dates = [start] + rebal_dates

    # Ensure the end date is included
    if rebal_dates[-1] != end:
        rebal_dates.append(end)

    # Initialize the dataset with a wider date range to avoid boundary errors
    start_date_large = start - pd.Timedelta(days=15)
    end_date_large = end + pd.Timedelta(days=15)
    data = data_modif.get_economic_cadran_data(economic_quadrant, start_date_large, end_date_large)
    full_idx = pd.date_range(start_date_large, end_date_large, freq="D")
    data = data.reindex(full_idx).ffill()


    # Check that the required tickers exist in the data
    for ticker in required_tickers:
        if ticker not in data.columns:
            raise KeyError(f"Ticker {ticker} is missing from the downloaded data.")

    # Loop over the rebalancing sub-periods
    performance_factor = 1.0

    for i in range(len(rebal_dates) - 1):

        date_start = rebal_dates[i]
        date_end   = rebal_dates[i + 1]

        # Calculation range periods
        num_days = (pd.to_datetime(date_end) - pd.to_datetime(date_start)).days
        data_size = max(num_days, 1)  # avoid zero-length windows

        if economic_quadrant == "Quadrant 3: Deflationary Bust" or economic_quadrant == "Quadrant 4: Deflationary Boom":

             # Compute the average bond yield over the period (simple average of FVX and TYX, in decimal form)
            bond_avg = ((data['^FVX'].loc[date_start:date_end].astype(float).squeeze() + data['^TYX'].loc[date_start:date_end].astype(float).squeeze()) / 2) / 100

            # Smooth bond yield with a rolling average
            bond_avg_period = (bond_avg.loc[date_start:date_end].rolling(window=data_size, min_periods=1).mean())
            last_bonds_mean = bond_avg_period.iloc[-1] if hasattr(bond_avg_period, 'iloc') and len(bond_avg_period) else 0.0

            # Compute daily compounded interest rate (in decimal form)
            annual_interest_rate = last_bonds_mean
            daily_interest_rate  = (1 + annual_interest_rate) ** (1 / 365) - 1
            last_bonds_growth    = (1 + daily_interest_rate) ** num_days - 1

        if economic_quadrant == "Quadrant 1: Inflationary Bust" or economic_quadrant == "Quadrant 2: Inflationary Boom":

            # Compute gold growth over the period (in decimal form)
            gold_data = data['GC=F'].loc[start_date:end_date].dropna()
            last_gold_growth = (gold_data.iloc[-1] - gold_data.iloc[0]) / gold_data.iloc[0]


        if economic_quadrant == "Quadrant 2: Inflationary Boom" or economic_quadrant == "Quadrant 4: Deflationary Boom":

            # Compute equity growth (S&P 500) over the period (in decimal form)
            equity_data = data['^GSPC'].loc[start_date:end_date].dropna()
            last_equity_growth = ((equity_data.iloc[-1] - equity_data.iloc[0]) / equity_data.iloc[0])

        # Apply performance rules depending on the economic quadrant
        if economic_quadrant == "Quadrant 1: Inflationary Bust" :
            performance_factor = performance_factor * (1 + last_gold_growth)
        if economic_quadrant == "Quadrant 2: Inflationary Boom" :
            performance_factor = performance_factor * (1 + (0.5 * last_gold_growth + 0.5 * last_equity_growth))
        if economic_quadrant == "Quadrant 3: Deflationary Bust":
            performance_factor = performance_factor * (1 + last_bonds_growth)
        if economic_quadrant == "Quadrant 4: Deflationary Boom":
            performance_factor = performance_factor * (1 + (0.5 * last_bonds_growth + 0.5 * last_equity_growth))

    final_money = float(money) * performance_factor
    performance_percentage = (final_money / float(money) - 1.0) * 100.0

    return final_money, performance_percentage, economic_quadrant

# Compute volatility of assets
def volatility(start_date, end_date):

    # Quadrant of the assets where we calculate the volatility (where we look for gold or equity) so take quadrant 2
    quadrant = "Quadrant 2: Inflationary Boom"

    # Initialize data
    data = data_modif.get_economic_cadran_data(quadrant, start_date, end_date)

    # Compute volatility gold
    returns_gold = data['GC=F'].pct_change()
    vol_gold = returns_gold.std() * (len(returns_gold) ** 0.5)

    # Compute volatility equity
    returns_equity = data['^GSPC'].pct_change()
    vol_equity = returns_equity.std() * (len(returns_equity) ** 0.5)



    return vol_gold, vol_equity