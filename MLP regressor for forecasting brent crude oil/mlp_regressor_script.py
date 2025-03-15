import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import yfinance as yf
import joblib

# 1. Retrieve historical Brent crude oil data
brent = yf.download('BZ=F', start='2015-01-01', end='2025-01-01', interval='1d', auto_adjust=False)
if 'Adj Close' in brent.columns:
    brent = brent[['Adj Close']]
    brent.rename(columns={'Adj Close': 'Brent_Price'}, inplace=True)
brent.dropna(inplace=True)
#print(brent)

# 2. Choose economic and financial variables
selected_tickers = [
    '^GSPC', '^DJI', '^IXIC', 'GC=F', 'EURUSD=X', 'DX-Y.NYB', 'XAUUSD=X'
]

# Download data for selected tickers
dataframes = []
for ticker in selected_tickers:
    try:
        df_var = yf.download(ticker, start='2015-01-01', end='2025-01-01', interval='1d', auto_adjust=False)
        if 'Adj Close' in df_var.columns:
            df_var = df_var[['Adj Close']]
            df_var.rename(columns={'Adj Close': ticker}, inplace=True)
            dataframes.append(df_var)
    except Exception as e:
        print(f"Failed to download data for {ticker}: {e}")
    #print(df_var)

# Merge data on date
df = brent.copy()
for data in dataframes:
    df = df.join(data, how='outer')

# Remove columns with more than 95% missing values
df.dropna(thresh=len(df) * 0.95, axis=1, inplace=True)

# Remove rows with any remaining missing values
df.dropna(inplace=True)

df = df[df.index >= '2015-01-01']  # Restrict analysis from 2015 onwards
#print('\nDataframe final : \n')
#print(df)

# Check if Brent_Price is still in df
if 'Brent_Price' not in df.columns:
    raise ValueError("Brent_Price column was removed during cleaning. Check data sources.")

# 3. Prepare the data
features = [col for col in df.columns if col != 'Brent_Price']
X = df[features]
y = df['Brent_Price']

# Check if data is empty before normalization
if X.empty or y.empty:
    raise ValueError("No valid data available for training. Check data sources.")

# Normalize the data
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)

# Split into training (90%) and testing (10%) sets
test_size = 0.1
train_size = 1 - test_size
train_index = int(len(X_scaled) * train_size)

X_train, X_test = X_scaled[:train_index], X_scaled[train_index:]
y_train, y_test = y[:train_index].values.ravel(), y[train_index:].values.ravel()

# 4. Neural Network (MLP) with two hidden layers
nn_model = MLPRegressor(hidden_layer_sizes=(200, 100), activation='relu', max_iter=500, random_state=42)
nn_model.fit(X_train, y_train)
predictions_nn = nn_model.predict(X_test)

# Calculate errors
absolute_errors = np.abs((y_test - predictions_nn) / y_test) * 100
mean_error = np.mean(absolute_errors)
max_error = np.max(absolute_errors)

print(f"Mean absolute error in percentage: {mean_error:.2f}%")
print(f"Max error on a single sample in percentage: {max_error:.2f}%")

# Save the trained model
joblib.dump(nn_model, "mlp_regressor_model.pkl")
print("Model saved as mlp_regressor_model.pkl")

# 5. Visualization of results with dates on x-axis
plt.figure(figsize=(12,6))
plt.plot(df.index[train_index:], y_test, label='Actual Price', alpha=0.7)
plt.plot(df.index[train_index:], predictions_nn, label='Neural Network Prediction', linestyle='dotted', alpha=0.7)
plt.legend()
plt.xlabel('Date')
plt.ylabel('Oil Price (USD)')
plt.title('Oil Price Prediction using Neural Network')
plt.xticks(rotation=45)
plt.show()
