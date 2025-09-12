import permanent_portofolio_simulations_librairies as lib

# 1 Selection of the quadrant
gold_bonds_ratio, gold_equity_ratio = lib.get_market_ratios('2010-01-01','2018-01-01')
current_quadrant = lib.determine_quadrant(gold_bonds_ratio, gold_equity_ratio)
print(f"Detected current quadrant : {current_quadrant}")

# 2 Test the strategy
print(lib.get_return_of_investments(100000,100,current_quadrant,'2010-01-01','2010-01-01'))