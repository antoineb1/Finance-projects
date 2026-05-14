import pickle
import pandas as pd
import matplotlib.pyplot as plt

data_gold = pickle.load(open("data_download_gold.pkl", "rb"))
price = data_gold["GC=F"].dropna()
running_max = price.cummax()
drawdown = price / running_max - 1

max_drawdown = drawdown.min()
max_drawdown_date = drawdown.idxmin()

df_gold = pd.DataFrame({
    "price": price,
    "running_max": running_max,
    "drawdown": drawdown,
    "drawdown_pct": drawdown * 100
})

print(df_gold)
print("\nMax drawdown :", round(max_drawdown * 100, 2), "%")
print("Date du max drawdown :", max_drawdown_date)

# Plot drawdown
plt.figure(figsize=(12, 5))
(df_gold["drawdown_pct"]).plot()
plt.title("Drawdown de l'or GC=F au cours du temps")
plt.ylabel("Drawdown (%)")
plt.xlabel("Date")
plt.grid(True)
plt.show()