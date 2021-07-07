import sys, pandas as pd, json
try:
    import simulation_configuration as sim_cfg
except:
    sys.path.append('N:/TESE/Bullwhip')
    import simulation_configuration as sim_cfg





def get_inventory_dataset():
    inventory_file = sim_cfg.inventory_file


    with open(inventory_file, 'r') as file:
        data=file.read()   #aqui entra como str

        data=json.loads(data)         #rebenta aqui com :    00
        df1 = pd.DataFrame([]) 
        for actor in data:
            for prod_list in data[actor]:
                for prod in prod_list:
                    df2 = pd.DataFrame( [ [ actor, prod, prod_list[prod] ]  ]  , columns=["Ator","Product", "Quantity"] )
                    print(df2)
                df1=df1.append(df2) 
        print(df1)    
        file.close
    
        # with open("inventario.txt", 'a') as f:
        #     f.write(df1.to_string())   #aqui entra como str

        # return df1.sort_values(by='Ator')


inventory_dataset= get_inventory_dataset()

# inventory_dataset_columns = inventory_dataset.columns
