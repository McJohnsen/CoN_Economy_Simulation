import pandas as pd

if __name__ == "__main__":
    data_table = pd.read_csv('../data/buildings.csv')
    data_table = data_table.set_index('abbreviation')
