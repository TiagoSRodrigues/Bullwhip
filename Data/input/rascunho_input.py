
import csv
import pandas as pd


file_path="n:/TESE/Bullwhip/data/input/input_data.csv"

# with open(file_path,"r") as csvfile:
#     data = csv.reader(csvfile, delimiter=',')
#     for row in data:
#         print(', '.join(row))

df = pd.read_csv(file_path, delimiter=";", decimal=".")
df['date'] = pd.to_datetime(df['date'])

print(df.describe())