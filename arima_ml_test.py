
import numpy as np
import cudf
from cuml.tsa.arima import ARIMA
from cuml.tsa.auto_arima import AutoARIMA

import pandas as pd

#utilidades
from datetime import datetime
from datetime import timedelta

def add_timestamps(serie):
    array_size = len(serie)-1
    now = datetime.now().date()
    
    timestamp = pd.date_range(end=now, start=now - timedelta(days = array_size)).to_frame(index=False, name="day")
       
    return pd.concat([timestamp, serie], axis=1)

#import data

base_file = "/rapids/data/input/real_data_interpolated.csv"

    
# base_df =  pd.read_csv(base_file)
# base_df.columns = ["value"]
# base_df = add_timestamps(base_df)
# base_df = base_df.set_index("day")


df = pd.read_csv(base_file).astype(np.float64)

print(df.tail)

model = AutoARIMA(df)
model.search( p=80, q=25,
             fit_intercept = "auto", seasonal_test="seas")
model.fit()


print(model.summary())


# forecast_df.columns = df.columns
# df.to_csv("forecasts.csv", index=False)