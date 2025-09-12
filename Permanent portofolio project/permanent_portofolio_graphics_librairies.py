import permanent_portofolio_simulations_librairies as lib
import matplotlib.pyplot as plt
import pandas as pd
import random
from typing import Iterable, List, Union

# Compute and show the results
def simulation(annees: Iterable[Union[int, str]],lookback_years,rebalance_days,money) :

    years=[]
    gb_ratios = []
    ge_ratios = []
    quadrants = []
    money_finals = []
    perfs = []
    all_years_vol_gold = []
    all_years_vol_equity = []

    # Init monay
    final_money = money

    for a in annees:
        y = int(a)
        # Fenêtre pour les ratios
        ratio_start = f"{y - lookback_years}-01-01"
        ratio_end   = f"{y}-01-01"
        # Fenêtre pour la perf de l'année
        year_start  = f"{y}-01-01"
        year_end    = f"{y+1}-01-01"

        # Quadrant 5 init management (change with strategy)
        # last_year_quadrant = None
        quadrant_5 = 0

        # 1) Ratios & cadran basé sur la fenêtre lookback
        gold_bonds_ratio, gold_equity_ratio = lib.get_market_ratios(ratio_start, ratio_end)
        #0gold_bonds_ratio, gold_equity_ratio = 10 *, 10 # Pour eviter les pourcentage
        quadrant = lib.determine_quadrant(gold_bonds_ratio, gold_equity_ratio)

        # Use the last year quadrant for this case but can change with the strategy
        if quadrant == "Quadrant 5: Transition Quadrant":

            # if last_year_quadrant is not None:
            #     #quadrant = last_year_quadrant

            quadrant_5= 1

            # else:
            #             # Random quadrant if last year quadrant is none
            #             quadrant = random.choice([
            #                 "Quadrant 1: Inflationary Bust",
            #                 "Quadrant 2: Inflationary Boom",
            #                 "Quadrant 3: Deflationary Bust",
            #                 "Quadrant 4: Deflationary Boom"
            #             ])

        # Put the quadrant in the memory for the next year (change with the strategy)
        #last_year_quadrant = quadrant

        # Compute money and perfroamnce
        if quadrant_5 == 1:
            final_money, performance_pct = final_money, 1
            quadrants.append("Quadrant 5: Transition Quadrant")

        else:
            final_money, performance_pct, _  = lib.get_return_of_investments(final_money, rebalance_days, quadrant, year_start, year_end)
            # Change tickers in str for the list
            quadrants.append(str(quadrant))

        # Compute volatility and add to the list of volatilities
        vol_gold, vol_equity = lib.volatility(year_start, year_end)

        # Add elements to the lists
        years.append(y)
        gb_ratios.append(gold_bonds_ratio)
        ge_ratios.append(gold_equity_ratio)
        money_finals.append(final_money)
        perfs.append(performance_pct)
        all_years_vol_gold.append(vol_gold)
        all_years_vol_equity.append(vol_equity)


    # Check if all the have the same size
    n = len(years)
    if not all(len(lst) == n for lst in [gb_ratios, ge_ratios, quadrants, money_finals, perfs, quadrants, all_years_vol_gold, all_years_vol_equity]):
        raise ValueError("Les listes n'ont pas toutes la même longueur. Vérifie tes 'append'.")

    # Show the list quadrants
    for i in range(len(years)):
        print(f"Année {years[i]} : {quadrants[i]} : ratio_gold_cash_bonds : {gb_ratios[i]} , ratio_equity : {ge_ratios[i]}  ")

    print('\n')

    # Show the list performance and money
    for i in range(len(years)):
        print(f"Année {years[i]} : performance :{perfs[i]} money : {money_finals[i]}")

    # plot ratios Gold/(Bonds or cash)
    plt.figure(figsize=(10, 4))
    plt.plot(years, gb_ratios, marker="o", label="Ratio Gold/(Bonds or cash)")
    plt.title("Indicateurs – Portefeuille permanent : Ratios Gold/(Bonds or cash)")
    plt.xlabel("Année")
    plt.ylabel("Ratio Gold/(Bonds or cash)")
    plt.grid(True, linestyle="--", linewidth=0.5, alpha=0.6)
    plt.legend()
    plt.tight_layout()

    # plot ratios Gold/Equity
    plt.figure(figsize=(10, 4))
    plt.plot(years, ge_ratios, marker="o", label="Ratio Gold/Equity",color="orange")
    plt.title("Indicateurs – Portefeuille permanent : Ratios Gold/Equity")
    plt.xlabel("Année")
    plt.ylabel("Ratio Gold/Equity")
    plt.grid(True, linestyle="--", linewidth=0.5, alpha=0.6)
    plt.legend()
    plt.tight_layout()

    # plot performance
    plt.figure(figsize=(10, 4))
    plt.plot(years, perfs, marker="x", linestyle="--", label="Perf annuelle (%)")
    plt.title("Indicateurs – Portefeuille permanent : Performance annuelle (%)")
    plt.xlabel("Année")
    plt.ylabel("Performance (%)")
    plt.grid(True, linestyle="--", linewidth=0.5, alpha=0.6)
    plt.legend()
    plt.tight_layout()

    # plot final money (€)
    plt.figure(figsize=(10, 4))
    plt.plot(years, money_finals, marker="s", linestyle=":", label="Valeur finale (€)")
    plt.title("Indicateurs – Portefeuille permanent : Valeur finale (€)")
    plt.xlabel("Année")
    plt.ylabel("€")
    plt.grid(True, linestyle="--", linewidth=0.5, alpha=0.6)
    plt.legend()
    plt.tight_layout()

    # plot asset volatility (gold)
    plt.figure(figsize=(10, 4))
    plt.plot(years, all_years_vol_gold, marker="s", linestyle=":", label="Volatilite or")
    plt.title("Indicateurs – Portefeuille permanent : Volatilité or")
    plt.xlabel("Année")
    plt.ylabel("Vol or")
    plt.grid(True, linestyle="--", linewidth=0.5, alpha=0.6)
    plt.legend()
    plt.tight_layout()

    # plot asset volatility (equity)
    plt.figure(figsize=(10, 4))
    plt.plot(years, all_years_vol_equity, marker="s", linestyle=":", label="Volatilite actions")
    plt.title("Indicateurs – Portefeuille permanent : Volatilité actions")
    plt.xlabel("Année")
    plt.ylabel("Vol actions")
    plt.grid(True, linestyle="--", linewidth=0.5, alpha=0.6)
    plt.legend()
    plt.tight_layout()

    plt.show()

    return years, gb_ratios, ge_ratios, quadrants, money_finals, perfs

# Example
liste_annee = list(range(2005, 2026))   # 1995 to 2025 include
#print(liste_annee)
resultats = simulation(liste_annee, 15, 100, 100000)
