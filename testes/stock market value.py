import pandas as pd
import datetime
import numpy as np
import matplotlib.pyplot as plt
from pandas.plotting import scatter_matrix
import yfinance as yf


start = "1990-01-01"
end = '2022-1-01'
tcs = yf.download('AAPL',start,end)
infy = yf.download('MSFT',start,end)
wipro = yf.download('TSM',start,end)
wipro = yf.download('TSM',start,end)

tcs['Volume'].plot(label = 'TCS', figsize = (15,7))
infy['Volume'].plot(label = "Infosys")
wipro['Volume'].plot(label = 'Wipro')
print(type(tcs))