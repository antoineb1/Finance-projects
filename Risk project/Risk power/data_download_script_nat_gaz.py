import data_download_librairies_nat_gaz as data_lib
import pickle

CACHE_PATH = "data_download_nat_gaz.pkl"  # the file used as cache

if __name__ == "__main__":

    # Download the data and store it in memory (take more large than the simulations date at least 1 month before and 1 month after)
    data_download_global = data_lib.download_all_data("2022-01-01", "2026-01-01")

    # Check if the datas are empty
    if not data_download_global.empty:

        # Save the variable into the cache
        with open(CACHE_PATH, "wb") as f:   # wb = write binary
            pickle.dump(data_download_global, f)
        print("Cache created:", CACHE_PATH)

    else:
        print('Error during the download')

# Load the variable back from the cache
with open(CACHE_PATH, "rb") as f:       # rb = read binary
    data_download_global = pickle.load(f)
#print("Cache loaded into memory and type is :", type(data_download_global))