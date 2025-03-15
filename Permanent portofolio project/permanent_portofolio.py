import permanent_portofolio_librairies as lib

# 1 Selection of the quadrant
gold_bonds_ratio, gold_equity_ratio = lib.get_market_ratios('2021-01-01','2025-01-01')
current_quadrant = lib.determine_quadrant(gold_bonds_ratio, gold_equity_ratio)
print(f"Detected current quadrant : {current_quadrant}")

# 2 Selection of the portfolio's weights
lib.get_final_portfolio(current_quadrant,'2011-01-01','2025-01-01')