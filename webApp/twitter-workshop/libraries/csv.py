# Operations with CSV files

import pandas as pd
import csv
import re


# Append a list to a csv file
def append_csv(file, data):
    with open(file, 'a') as f:
        writer = csv.writer(f)
        writer.writerow(data)


# Extract some columns from a CSV file to a multi-dimensional array
def get_data(file, columns):
    data = pd.read_csv(file)
    r_data = []
    
    for row in data.itertuples():
        row_data = []
        for col in columns:
            row_data.append(getattr(row, col))
        r_data.append(row_data)

    return r_data
