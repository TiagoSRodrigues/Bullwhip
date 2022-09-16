import numpy as np
import pandas as pd
import scipy
import statsmodels.api as sm
import matplotlib.pyplot as plt
import seaborn as sns
import sklearn
from statsmodels.tsa.arima_model import ARIMA
# from arch import arch_model
import seaborn as sns
# import yfinance
import warnings
warnings.filterwarnings("ignore")
sns.set()

file = "N:\TESE\Bullwhip\data\input\S4248SM144NCEN.csv"




df= pd.read_csv(file)
df.columns=["date","value"]
print(df.head)

