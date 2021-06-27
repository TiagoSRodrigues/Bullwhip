# from simulation_configuration import source_data
import datetime, pandas as pd, random
from.import logging_management as logs

def get_input(days=None, min=None, max=None):
    
    if days == None:
        good_values, errors, values = check_input_datafile()
        return values
    else:
        values = []
        for i in range(days):
            values.append(random.randint(min, max))
        return values

    

def check_input_datafile():
    errors=0
    good_values=0
    values=[]
    try:
        data=open(source_data) 
        for line in data:
            try:
                date, val, *_ = [item.strip() for item in line.split(',')]
                date_check=datetime.datetime.strptime(date, '%Y-%m-%d')
                values.append(float(val))
                good_values+=1
            except:
                errors+=1

    finally:
        logs.log(debug_msg = "DATA_INPUT  input file checked good values: "+str(good_values)+"  errors: "+str(errors))
    
    return good_values, errors, values
    

