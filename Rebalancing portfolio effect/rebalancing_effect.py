import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go


## Paramètres
n = 300 # nombre de périodes simulées
capital_initial = 1000

annual_return_1 = 0.05
annual_return_2 = 0.05

annual_vol_1 = 0.18
annual_vol_2 = 0.12

mu_1 = (1 + annual_return_1)**(1/24) - 1 # half month
mu_2 = (1 + annual_return_2)**(1/24) - 1

sigma_1 = annual_vol_1 / np.sqrt(24)
sigma_2 = annual_vol_2 / np.sqrt(24)

noise_to_signal = 0.5

df = 5
rho = -1   # corrélation

## Calcul

returns_capital_1_results = []
returns_portfolio_results = []
nb_simus = 50000  # nb de simus Monte Carlo

for simu in range(nb_simus):

    student_1 = np.random.standard_t(df, n)

    bruit = np.random.standard_t(df, n)
    student_2 = (rho * student_1 + noise_to_signal * bruit)/(abs(rho)+noise_to_signal)

    returns_1 = mu_1 + sigma_1 * student_1
    returns_2 = mu_2 + sigma_2 * student_2

    capital_1 = capital_initial * np.cumprod(1 + returns_1)
    capital_2 = capital_initial * np.cumprod(1 + returns_2)
    capital_portfolio = 0.5 * capital_1 + 0.5 * capital_2

    rendement_capital_1 = capital_1[-1] / capital_initial - 1
    returns_capital_1_results.append(rendement_capital_1)
    rendement_portfolio = capital_portfolio[-1] / capital_initial - 1
    returns_portfolio_results.append(rendement_portfolio)


returns_capital_1_results = np.array(returns_capital_1_results)
returns_portfolio_results = np.array(returns_portfolio_results)

print("===== Actif 1 =====")
print("Rendement moyen actif 1 :", np.mean(returns_capital_1_results))
print("Rendement médian actif 1 :", np.median(returns_capital_1_results))
print("Écart-type actif 1 :", np.std(returns_capital_1_results, ddof=1))
print("Rendement 5% percentile actif 1 :", np.percentile(returns_capital_1_results, 5))
print("Rendement 95% percentile actif 1 :", np.percentile(returns_capital_1_results, 95))

print("\n===== Portefeuille =====")
print("Rendement moyen portefeuille :", np.mean(returns_portfolio_results))
print("Rendement médian portefeuille :", np.median(returns_portfolio_results))
print("Écart-type portefeuille :", np.std(returns_portfolio_results, ddof=1))
print("Rendement 5% percentile portefeuille :", np.percentile(returns_portfolio_results, 5))
print("Rendement 95% percentile portefeuille :", np.percentile(returns_portfolio_results, 95))

fig = go.Figure()

fig.add_trace(go.Histogram(
    x=returns_capital_1_results,
    histnorm="probability density",
    nbinsx=80,
    name="Actif 1",
    opacity=0.55
))

fig.add_trace(go.Histogram(
    x=returns_portfolio_results,
    histnorm="probability density",
    nbinsx=80,
    name="Portefeuille 50/50",
    opacity=0.55
))

fig.update_layout(
    title="Densité des rendements finaux",
    xaxis_title="Rendement final",
    yaxis_title="Densité",
    barmode="overlay",
    template="plotly_white",
    legend_title="Cliquer pour afficher/masquer"
)

fig.write_html("density_returns.html",include_plotlyjs="cdn",full_html=True,auto_open=True)
