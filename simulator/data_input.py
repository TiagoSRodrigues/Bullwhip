# from simulation_configuration import source_data
import datetime, pandas as pd, random
import sys
import math
import numpy as np
# from.import logging_management as logs




# with open(file_path,"r") as csvfile:
#     data = csv.reader(csvfile, delimiter=',')
#     for row in data:
#         print(', '.join(row))

# df = pd.read_csv(file_path, delimiter=";", decimal=".")
# df['date'] = pd.to_datetime(df['date'])

# print(df.describe())


def get_input(input_type,  days=None, min=None, max=None, filename=None):
    
    if input_type == "file":
        values=get_raw_data(filename)
        if days is None:
            return values
        return values[-days:]
        
    if input_type == "file_old":
        good_values, errors, values = check_input_datafile()
        
        if errors >0:
            print("erros: {} good values: {}". format(errors, good_values))
        if days is None:
            return values
        return values[-days:]

    if input_type == "constant":
        a = np.empty(days, dtype=np.int64)
        a.fill(min)
        return a

    
    
    if input_type == "sequencial":
        np.linspace(min,max, num=max-min, endpoint=False,  dtype=int, axis=0)
            
    if input_type == "triangular":
        values = []
        slope  = 1
        x = min
        while len(values) < days:
            values.append(x)
            x = x + 1 * slope
        
            if x == max:
                slope = -1
            elif x == min:
                slope = 1
        return values
        
    values = []
    for i in range(days):
        values.append(random.randint(min, max))
    return values

    
def get_raw_data(filename):
    if "real" in filename:
        filepath = sys.path[0] + "/data/input/real_data_interpolated.csv"
    else:
        filepath = sys.path[0] + "/data/input/data_amplified.csv"

    from numpy import genfromtxt
    data = genfromtxt(filepath, delimiter='')
    data=data[~np.isnan(data)]
    return data
    
    
def check_input_datafile():
    def better_round(value):
        if value%1 *10 < 5:
            return math.floor(value)
        return math.ceil(value)
    errors=-1 #(menos um porque os headers vão dar erro)
    good_values=0
    values=[]
    
    scale_fator=100 #multiplica o valor da cotação por dez
    
    data=open(cambio_data)
    for line in data:
        try:
            date, val, *_ = [item.strip() for item in line.split(';')]
            #date_check=datetime.datetime.strptime(date, '%Y-%m-%d')
            values.append(better_round(float(val)*scale_fator))
            good_values+=1
            # print(val)
        except:
            errors+=1

  
        # logs.log(debug_msg = "DATA_INPUT  input file checked good values: "+str(good_values)+"  errors: "+str(errors))
    data.close()
    return good_values, errors, values
    
