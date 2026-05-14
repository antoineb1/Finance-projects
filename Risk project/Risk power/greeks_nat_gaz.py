import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import norm
from scipy.optimize import brentq

# =========================
# Load data
# =========================

data_nat_gaz = pickle.load(open("data_download_nat_gaz.pkl", "rb"))

df_option = pd.DataFrame()
df_option["future_price_M_1"] = data_nat_gaz["NG=F"].dropna().astype(float)

# =========================
# Paramètres option
# =========================

option_type = "call"   # "call" ou "put"

K = df_option["future_price_M_1"].iloc[-1]   # Strike ATM aujourd'hui
T = 30 / 365                                 # Maturité 30 jours
r = 0.04                                     # Taux sans risque

# Si tu es acheteur de l'option : quantity = 1
# Si tu es vendeur / émetteur : quantity = -1
quantity = 1

# Taille du contrat
# Pour l'instant 1 pour simplifier
contract_size = 1

# =========================
# Fonctions Black-76
# =========================

def black76_call(F, K, T, r, sigma):
    sqrt_T = np.sqrt(T)
    discount = np.exp(-r * T)

    d1 = (np.log(F / K) + 0.5 * sigma**2 * T) / (sigma * sqrt_T)
    d2 = d1 - sigma * sqrt_T

    price = discount * (F * norm.cdf(d1) - K * norm.cdf(d2))
    return price


def black76_put(F, K, T, r, sigma):
    sqrt_T = np.sqrt(T)
    discount = np.exp(-r * T)

    d1 = (np.log(F / K) + 0.5 * sigma**2 * T) / (sigma * sqrt_T)
    d2 = d1 - sigma * sqrt_T

    price = discount * (K * norm.cdf(-d2) - F * norm.cdf(-d1))
    return price


def implied_vol_black76(market_price, F, K, T, r, option_type="call"):
    def objective(sigma):
        if option_type == "call":
            return black76_call(F, K, T, r, sigma) - market_price
        elif option_type == "put":
            return black76_put(F, K, T, r, sigma) - market_price
        else:
            raise ValueError("option_type doit être 'call' ou 'put'")

    try:
        implied_vol = brentq(objective, 0.0001, 5.0)
        return implied_vol
    except ValueError:
        return np.nan

# =========================
# 1) Simuler une fausse volatilité implicite
# =========================

np.random.seed(42)

df_option["sigma_implied_fake"] = np.random.uniform(
    low=0.40,
    high=1.20,
    size=len(df_option)
)

# =========================
# 2) Calculer un faux prix de marché d'option
# =========================

if option_type == "call":
    df_option["option_price_market_fake"] = [
        black76_call(F, K, T, r, sigma)
        for F, sigma in zip(
            df_option["future_price_M_1"],
            df_option["sigma_implied_fake"]
        )
    ]

elif option_type == "put":
    df_option["option_price_market_fake"] = [
        black76_put(F, K, T, r, sigma)
        for F, sigma in zip(
            df_option["future_price_M_1"],
            df_option["sigma_implied_fake"]
        )
    ]

else:
    raise ValueError("option_type doit être 'call' ou 'put'")

# =========================
# 3) Retrouver la vol implicite depuis le prix d'option
# =========================

df_option["sigma_implied_retrieved"] = [
    implied_vol_black76(price, F, K, T, r, option_type)
    for price, F in zip(
        df_option["option_price_market_fake"],
        df_option["future_price_M_1"]
    )
]

# =========================
# 4) Comparaison sigma fake vs sigma retrouvée
# =========================

df_option["difference_sigma"] = (
    df_option["sigma_implied_retrieved"]
    - df_option["sigma_implied_fake"]
)

# =========================
# 5) Calcul des Greeks avec sigma retrouvée
# =========================

df_option["sigma_used"] = df_option["sigma_implied_retrieved"]

df_option["sqrt_T"] = np.sqrt(T)
df_option["discount"] = np.exp(-r * T)

df_option["d1"] = (
    np.log(df_option["future_price_M_1"] / K)
    + 0.5 * df_option["sigma_used"]**2 * T
) / (
    df_option["sigma_used"] * df_option["sqrt_T"]
)

df_option["d2"] = (
    df_option["d1"]
    - df_option["sigma_used"] * df_option["sqrt_T"]
)

# =========================
# Delta
# =========================

if option_type == "call":
    df_option["delta"] = (
        df_option["discount"]
        * norm.cdf(df_option["d1"])
    )

elif option_type == "put":
    df_option["delta"] = (
        -df_option["discount"]
        * norm.cdf(-df_option["d1"])
    )

# =========================
# Gamma
# =========================

df_option["gamma"] = (
    df_option["discount"]
    * norm.pdf(df_option["d1"])
    / (
        df_option["future_price_M_1"]
        * df_option["sigma_used"]
        * df_option["sqrt_T"]
    )
)

# =========================
# Vega
# =========================

df_option["vega"] = (
    df_option["discount"]
    * df_option["future_price_M_1"]
    * norm.pdf(df_option["d1"])
    * df_option["sqrt_T"]
)

# Vega pour +1 point de volatilité
# Exemple : 80% -> 81%
df_option["vega_1pct"] = df_option["vega"] * 0.01

# =========================
# Theta
# =========================

df_option["theta"] = (
    -df_option["discount"]
    * df_option["future_price_M_1"]
    * norm.pdf(df_option["d1"])
    * df_option["sigma_used"]
    / (2 * df_option["sqrt_T"])
    + r * df_option["option_price_market_fake"]
)

# Theta par jour
df_option["theta_1day"] = df_option["theta"] / 365

# =========================
# Rho
# =========================

df_option["rho"] = -T * df_option["option_price_market_fake"]

# Rho pour +1 bp de taux
# Exemple : 4.00% -> 4.01%
df_option["rho_1bp"] = df_option["rho"] * 0.0001

# =========================
# 6) Positions / exposures de Greeks
# =========================

df_option["option_position_value"] = (
    df_option["option_price_market_fake"]
    * quantity
    * contract_size
)

df_option["delta_position"] = (
    df_option["delta"]
    * quantity
    * contract_size
)

df_option["delta_exposure"] = (
    df_option["delta"]
    * df_option["future_price_M_1"]
    * quantity
    * contract_size
)

df_option["gamma_position"] = (
    df_option["gamma"]
    * quantity
    * contract_size
)

df_option["gamma_exposure"] = (
    df_option["gamma"]
    * df_option["future_price_M_1"]**2
    * quantity
    * contract_size
)

df_option["vega_position"] = (
    df_option["vega"]
    * quantity
    * contract_size
)

df_option["vega_exposure_1pct"] = (
    df_option["vega_1pct"]
    * quantity
    * contract_size
)

df_option["theta_position_1day"] = (
    df_option["theta_1day"]
    * quantity
    * contract_size
)

df_option["rho_position_1bp"] = (
    df_option["rho_1bp"]
    * quantity
    * contract_size
)

# =========================
# 7) Affichage
# =========================

print("\nColonnes du DataFrame :")
print(df_option.columns)

print("\nDernières lignes :")
print(df_option[[
    "future_price_M_1",
    "option_price_market_fake",
    "sigma_implied_fake",
    "sigma_implied_retrieved",
    "difference_sigma",
    "delta",
    "gamma",
    "vega_1pct",
    "theta_1day",
    "rho_1bp",
    "delta_exposure",
    "gamma_exposure",
    "vega_exposure_1pct",
    "theta_position_1day",
    "rho_position_1bp"
]].tail())

print("\nRésumé dernière date :")
print("Dernier prix future :", round(df_option["future_price_M_1"].iloc[-1], 4))
print("Strike K :", round(K, 4))
print("Faux prix option :", round(df_option["option_price_market_fake"].iloc[-1], 6))
print("Sigma fake :", round(df_option["sigma_implied_fake"].iloc[-1], 6))
print("Sigma retrouvée :", round(df_option["sigma_implied_retrieved"].iloc[-1], 6))
print("Erreur sigma :", round(df_option["difference_sigma"].iloc[-1], 10))
print("Delta exposure :", round(df_option["delta_exposure"].iloc[-1], 6))
print("Gamma exposure :", round(df_option["gamma_exposure"].iloc[-1], 6))
print("Vega exposure 1% :", round(df_option["vega_exposure_1pct"].iloc[-1], 6))
print("Theta position 1 day :", round(df_option["theta_position_1day"].iloc[-1], 6))
print("Rho position 1 bp :", round(df_option["rho_position_1bp"].iloc[-1], 10))

# =========================
# 8) Une seule figure avec 3 subplots
# =========================

greek_position_cols = [
    "delta_exposure",
    "gamma_exposure",
    "vega_exposure_1pct",
    "theta_position_1day",
    "rho_position_1bp"
]

# Base 100 robuste pour les Greeks
df_greeks_base100 = df_option[greek_position_cols].copy()

for col in greek_position_cols:
    first_valid_value = df_greeks_base100[col].replace(0, np.nan).dropna().iloc[0]
    df_greeks_base100[col] = df_greeks_base100[col] / first_valid_value * 100

# Création d'une seule figure avec 3 graphiques
fig, axes = plt.subplots(
    nrows=3,
    ncols=1,
    figsize=(14, 12),
    sharex=True
)

# -------------------------
# 1) Prix du future
# -------------------------

df_option["future_price_M_1"].plot(ax=axes[0])

axes[0].set_title("Prix du future Nat Gas M-1")
axes[0].set_ylabel("Future price")
axes[0].grid(True)

# -------------------------
# 2) Faux prix de l'option
# -------------------------

df_option["option_price_market_fake"].plot(ax=axes[1])

axes[1].set_title("Faux prix de marché de l'option - Black 76")
axes[1].set_ylabel("Option price")
axes[1].grid(True)

# -------------------------
# 3) Positions des Greeks en base 100
# -------------------------

for col in greek_position_cols:
    df_greeks_base100[col].plot(ax=axes[2], label=col)

axes[2].set_title("Positions des Greeks en base 100")
axes[2].set_ylabel("Base 100")
axes[2].set_xlabel("Date")
axes[2].legend()
axes[2].grid(True)

plt.tight_layout()
plt.show()