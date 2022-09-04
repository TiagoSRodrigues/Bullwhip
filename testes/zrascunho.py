import keras
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

#utilidades
from datetime import datetime
from datetime import timedelta

#seasonal_decompose
import pmdarima as pm
from statsmodels.tsa.stattools import adfuller
from matplotlib.pylab import rcParams


def add_timestamps(serie):
    array_size = len(serie)-1
    now = datetime.now().date()
    
    timestamp = pd.date_range(end=now, start=now - timedelta(days = array_size)).to_frame(index=False, name="day")
       
    return pd.concat([timestamp, serie], axis=1)



#import data
base_file = "N:\\TESE\\Bullwhip\\data\\input\\real_data_interpolated.csv"

    
base_df =  pd.read_csv(base_file)
base_df.columns = ["value"]
base_df = add_timestamps(base_df)
base_df = base_df.set_index("day")



#Determine rolling statistics
base_df["rolling_avg"] = base_df["value"].rolling(window=365).mean() #window size 365 denotes 12 months, giving rolling mean at yearly level
base_df["rolling_std"] = base_df["value"].rolling(window=365).std()


def Plot_rolling_statistics():
    #Plot rolling statistics
    plt.figure(figsize=(15,7))
    plt.plot(base_df["value"], color='#379BDB', label='Original')
    plt.plot(base_df["rolling_avg"], color='#D22A0D', label='Rolling Mean')
    plt.plot(base_df["rolling_std"], color='#142039', label='Rolling Std')
    plt.legend(loc='best')
    plt.title('Rolling Mean & Standard Deviation')
    # plt.show()


def p_test(max_lag):
    #Augmented Dickey–Fuller test:
    print('Results of Dickey Fuller Test:')
    dftest = adfuller(base_df['value'], maxlag=max_lag)


    dfoutput = pd.Series(dftest[0:4], index=['Test Statistic','p-value','#Lags Used','Number of Observations Used'])
    
    for key,value in dftest[4].items():
        dfoutput['Critical Value (%s)'%key] = value
        
    print(dfoutput)

## o valhor 110 é o ideal para dar os P = 0.999
# for i in range(110,111,1):
#     p_test(i)
    
#Standard ARIMA Model
ARIMA_model = pm.auto_arima(base_df["value"],
                            start_p=100, 
                            start_q=25,
                            test='kpss', # use adftest to find optimal 'd'
                            max_p=120, max_q=35, # maximum p and q
                            #  m=1, # frequency of series (if m==1, seasonal is set to FALSE automatically)
                            d=None,# let model determine 'd'
                            seasonal=False, # No Seasonality for standard ARIMA
                            trace=False, #logs 
                            error_action='warn', #shows errors ('ignore' silences these)
                            suppress_warnings=True,
                            stepwise=True)


ARIMA_model.plot_diagnostics(figsize=(15,12))
# Plot_rolling_statistics()

plt.plot(pd.read_csv("forecasts.csv"))


plt.show()