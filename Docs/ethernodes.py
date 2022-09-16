import json
from matplotlib.font_manager import json_dump
import requests
import sys
import os
import pandas as pd
import numpy as np

DATA_DIRECTORY = sys.path[0]+"\\eth_data"

columns = "columns[0]\
[data]=id&columns[0][name]=&columns[0][searchable]=true&\columns[0][orderable]=true&columns[0][search][value]=&columns[0][search][regex]=false&columns[1]\
[data]=host&columns[1][name]=&columns[1][searchable]=true&columns[1][orderable]=true&columns[1][search][value]=&columns[1][search][regex]=false&columns[2]\
[data]=isp&columns[2][name]=&columns[2][searchable]=true&columns[2][orderable]=true&columns[2][search][value]=&columns[2][search][regex]=false&columns[3]\
[data]=country&columns[3][name]=&columns[3][searchable]=true&columns[3][orderable]=true&columns[3][search][value]=&columns[3][search][regex]=false&columns[4]\
[data]=client&columns[4][name]=&columns[4][searchable]=true&columns[4][orderable]=true&columns[4][search][value]=&columns[4][search][regex]=false&columns[5]\
[data]=clientVersion&columns[5][name]=&columns[5][searchable]=true&columns[5][orderable]=true&columns[5][search][value]=&columns[5][search][regex]=false&columns[6]\
[data]=os&columns[6][name]=&columns[6][searchable]=true&columns[6][orderable]=true&columns[6][search][value]=&columns[6][search][regex]=false&columns[7]\
[data]=lastUpdate&columns[7][name]=&columns[7][searchable]=true&columns[7][orderable]=true&columns[7][search][value]=&columns[7][search][regex]=false&columns[8]\
[data]=inSync&columns[8][name]=&columns[8][searchable]=true&columns[8][orderable]=true&columns[8][search][value]=&columns[8][search][regex]=false&order[0][column]=0&order[0][dir]=asc"

def prepare_invoke_request( columns, start, end):
    url= "https://ethernodes.org/data?draw=2&{}&start={}&length={}&search[value]=&search[regex]=false&_=1659869648696".format(columns, start, end)
    req = requests.get(url=url)
    return req.text  
        
    
def save_to_file(data, filename):
    with open(filename, "w") as f:
        f.write(data)





def get_new_data():
    for i in range(0, 6000, 100):
        data = prepare_invoke_request(columns, i, i+100)
        save_to_file(data, "{}\\eth_data\\ethernodes_{}_{}.json".format(sys.path[0],i,i+100))



def load_data_from_json(filename):
    with open(filename, "r") as f:
        data= json.loads(f.read())
        return data 

def save_data_to_json(data, filename):
    data=str(data).replace("'", '"')
    with open(DATA_DIRECTORY+"\\"+filename, 'w') as outfile:
        json.dump(data, outfile)
    print("file {} saved".format(filename))
    


def load_data_to_pandas(directory):
    files = os.listdir(directory)
    data = []
    for file in files:
        data.append(
                pd.DataFrame(
                    load_data_from_json(directory+"\\"+file)["data"]
            )
        )
        
    return pd.concat(data)

main_df = load_data_to_pandas(DATA_DIRECTORY)

df_countries = main_df[["country","id"]].groupby("country").count()


#installation pip install pycountry-convert

#function to convert to alpah2 country codes and continents
from pycountry_convert import country_alpha2_to_continent_code, country_name_to_country_alpha2
def get_continent(col):
    try:
        cn_a2_code =  country_name_to_country_alpha2(col)
    except:
        cn_a2_code = 'Unknown' 
    try:
        cn_continent = country_alpha2_to_continent_code(cn_a2_code)
    except:
        cn_continent = 'Unknown' 
    return (cn_a2_code, cn_continent)



#intall pip install geopy

#function to get longitude and latitude data from country name
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="http")

def geolocate(country):
    try:
        # Geolocate the center of the country
        loc = geolocator.geocode(country)
        # And return latitude and longitude
        return (loc.latitude, loc.longitude)
    except:
        # Return missing value
        return np.nan

# clean_country_data=""
# for country in df_countries.index:
#     new_line = str(country)+","+\
#         str(df_countries.loc[country][0])+","+\
#         str(geolocate(country))+","+\
#         str(df_countries.loc[country]["id"]) + ","
    
#     clean_country_data = clean_country_data+new_line+"\n"

# print("print:\n",clean_country_data, len(clean_country_data))


import plotly.express as px
import plotly.graph_objects as go

px.set_mapbox_access_token(open("N:\\TESE\\Bullwhip\\Docs\\mapbox_token").read())


map_data=pd.read_csv("N:\\TESE\\Bullwhip\\Docs\\clean_country_data.csv", encoding="iso-8859-1", sep=";")

df = px.data.gapminder()
fig = px.scatter_mapbox(map_data,
                     lat="lat",
                     lon="lon",
                     zoom=0,
                     size="size",
                     mapbox_style="light")
# fig.update_layout()



fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

fig.show()