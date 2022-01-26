from pmdarima.arima import auto_arima
import pandas as pd
data_file='N:\\TESE\\Bullwhip\\data\\input\\data_amplified.csv'



df = pd.read_csv(data_file, parse_dates=["date"],index_col="date")
