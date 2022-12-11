
from multiprocessing.sharedctypes import Value
from typing import final
from unittest import result
import yaml 
import os
import pandas as pd
os.system('cls') 
print("_"*200)

# get directories in path

first_actor = 1
last_actor = 5     
last_product= last_actor*1000+1

files_read = []


final_metrics={
    "lead_time_avg":None,
    "lead_time_std":None,
    "inventory_avg":None,
    "inventory_std":None,
    "delivered_products":None,
    "orders_delivered_ratio":None,
}

def get_files_in_folder(folder_path):
    files ={"inventory":[], "transactions":[], "orders":[]}
    files_in_folder = os.listdir(folder_path)
    
    for file_name in files_in_folder:
        if "inventory" in file_name:
            files["inventory"].append(file_name)
        if "transactions" in file_name:
            files["transactions"].append(file_name)
        if "orders" in file_name:
            files["orders"].append(file_name)
    
    return files


def read_simulation_record_json(file_path):
    ''' The simulations saves the data in dicts, but the json module can't read dicts, so we need to convert them to strings'''
    with open(file_path, "r") as file:
        data = file.read()
        data= data.replace("'",'"')[:-2].replace("\n",'').replace(" ",'')
        
        data = '{"data":[' + data + ']}'
        return data

# transactions
def get_transactions_df(file_path):
    files_read.append(file_path)
    data = read_simulation_record_json(file_path)
    transactions = pd.read_json(data, orient="split")
    
    # ignora o ultimo ator
    transactions = transactions[transactions['receiver'] < last_actor]

    # inventories[actor] = pd.concat([inventories[actor].drop(['inventory'], axis=1), inventories[actor]['inventory'].apply(pd.Series)], axis=1)
    # transactions.sort_values(by=["deliver_day", "receiver"], inplace=True)
    return transactions
    
def get_lead_time(transactions=None):
    if transactions is None:
        transactions = get_transactions_df(f"{simulation__results_path}\\{all_files['transactions'][0]}")
    return transactions[['lead_time']].mean()[0], transactions[['lead_time']].std()[0]

def get_delivered_transactions(transactions=None):
    if transactions is None:
        transactions = get_transactions_df(f"{simulation__results_path}\\{all_files['transactions'][0]}")
    return transactions[['quantity']].sum()[0], transactions[['quantity']].mean()[0], transactions[['quantity']].std()[0]


def get_client_final_inventary(file_path):

    transactions = get_transactions_df(file_path)
    final_client = transactions[transactions['receiver']==0]
    return  f"{final_client[['lead_time']].mean()[0]},{final_client[['lead_time']].std()[0]}, {final_client[['quantity']].sum()[0]}, {final_client[['theoretical_lead']].mean()[0]},{final_client[['theoretical_lead']].std()[0]}, {final_client[['delivered']].sum()[0]}\n"

# orders
def get_combined_orders_df():
    orders = pd.DataFrame()
    for file in all_files['orders']:
        # ifgora no primeito ator
        if f"actor_{first_actor}" in file:
            continue
        files_read.append(file)
        actor_orders=  pd.read_csv(f"{simulation__results_path}\\{file}", names=["Criation_Time", "Product", "Qty", "Client", "Order_id", "Status", "Notes"], index_col=False)
        actor_orders['actor'] = file.split("_")[3]
        orders = pd.concat([orders, actor_orders])
        
        orders = orders.drop(['Notes'], axis=1)
        orders.to_csv(f"N:\\TESE\\Bullwhip\\testes\\orders.csv", index=False)
        
    return orders

def orders_delivered_ratio():
    orders = get_combined_orders_df()
    orders_delivered = orders[orders['Status']==9]
    return len(orders_delivered)/len(orders)*100

# inventory
def get_combined_inventory_df():
    inventories = pd.DataFrame()
    for file in all_files['inventory']:
        #ignora o ultimo ator
        if f"actor_{last_actor}" in file:
            continue
        files_read.append(file)
        data = read_simulation_record_json(f"{simulation__results_path}\\{file}")
        actor_inventory = pd.read_json(data, orient="split")
        actor_inventory = pd.concat([actor_inventory.drop(['inventory'], axis=1), actor_inventory['inventory'].apply(pd.Series)], axis=1)
        inventories = pd.concat([inventories, actor_inventory])
    
    inventories.to_csv(f"N:\\TESE\\Bullwhip\\testes\\main_inventories.csv", index=False)
    return inventories.describe()


# utilitieis
def get_inventory_metrics():
    main_inventory = get_combined_inventory_df()
    last_product =  max([int(i) for i in main_inventory.columns if '1' in i])
    main_inventory = main_inventory.drop([str(last_product)], axis=1)
    main_mean = main_inventory.mean().mean()
    main_std = main_inventory.std().std()
    return main_mean, main_std
    
def get_simulation_config():
    with open(f"{simulation__results_path}\\simulation_config.yaml", "r") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
    return config

def update_metrics():
    final_metrics['lead_time_avg']=get_lead_time()[0]
    final_metrics['lead_time_std']=get_lead_time()[1]
    final_metrics['delivered_products']=get_delivered_transactions()[0]
    final_metrics['delivered_avg']=get_delivered_transactions()[1]
    final_metrics['delivered_std']=get_delivered_transactions()[2]
    final_metrics['orders_delivered_ratio']=orders_delivered_ratio()
    final_metrics['inventory_avg']=get_inventory_metrics()[0]
    final_metrics['inventory_std']=get_inventory_metrics()[1]

def pritty_print_final_metrics():
    update_metrics()
    configs= get_simulation_config()
    
    print(f"     Simulation Configs:","-"*100, sep="\n")
    print( 'actors:            ', configs['actors'])    
    print( 'simulation mode    ', configs['Simulation_mode'])    
    print( 'days:              ', configs['days'])    
    print( 'simulation_id:     ', configs['simulation_id'])    
     
    print("\nFinal Metrics\n", "-"*50, sep="\n")
    for metric, value in final_metrics.items():

        m_len= len(metric)
        
        title_len = 20
        metric_len = 12
    
        if isinstance(value, float):
            if value < 1000:
                value_str = f"{value:.2f}"
                spacing = " "*((title_len-m_len)+(metric_len - len(value_str)))
                print(f"{metric}:{spacing}{value_str}")
            else:
                value_str = f"{value:,.{0}f}".replace(",", " ")
                spacing = " "*((title_len-m_len)+(metric_len - len(value_str)))
                print(f"{metric}:{spacing}{value_str}")
                
        else:
            value_str =  f"{value:,.{0}f}".replace(",", " ")
            spacing = " "*((title_len-m_len)+(metric_len -len(value_str)))
            print(f"{metric}:{spacing}{value_str}")
    print("\n\n\n")
    for file in files_read:
        print(file)
        
def print_final_metrics():
    
    update_metrics()
    
    configs= get_simulation_config()
    
    
    
    actors_config_file = configs['actors'].split("//")[-1].split(".")[0]
    
    compiled= f"sim_{configs['simulation_id']} mode_{configs['Simulation_mode']} days_{configs['days']} {actors_config_file},"
    
    print(f"     Simulation Configs:","-"*100, sep="\n")
    print( 'actors:            ', configs['actors'])    
    print( 'simulation mode    ', configs['Simulation_mode'])    
    print( 'days:              ', configs['days'])    
    print( 'simulation_id:     ', configs['simulation_id'])    
     
    print("\nFinal Metrics\n", "-"*50, sep="\n")
    
    
    for metric, value in final_metrics.items():
        compiled += f"{value},"
        m_len= len(metric)
        
        title_len = 20
        metric_len = 12
    
        if isinstance(value, float):
            if value < 1000:
                value_str = f"{value:.2f}"
                spacing = " "*((title_len-m_len)+(metric_len - len(value_str)))
                print(f"{metric}:{spacing}{value_str}")
            else:
                value_str = f"{value:,.{0}f}".replace(",", " ")
                spacing = " "*((title_len-m_len)+(metric_len - len(value_str)))
                print(f"{metric}:{spacing}{value_str}")
                
        else:
            value_str =  f"{value:,.{0}f}".replace(",", " ")
            spacing = " "*((title_len-m_len)+(metric_len -len(value_str)))
            print(f"{metric}:{spacing}{value_str}")
    print("\n\n\n")

    return compiled+"\n"
        
        
        
        
        
        
        
        
        
        
        
        
        
        





all_sims = [name for name in os.listdir("N:\\TESE\\Bullwhip\\data\\results\\")if os.path.isdir(os.path.join("N:\\TESE\\Bullwhip\\data\\results\\", name))]
# print_final_metrics()
results = "Results:\n lead_time_mean, lead_time std, quantity sum, theoretical_lead mean, theoretical_lead std, delivered sum \n"
final_results = "final_results\n"
for sim in all_sims:

    print(sim)
    simulation__results_path = f"N:\\TESE\\Bullwhip\\data\\results\\{sim}"
    all_files = get_files_in_folder(simulation__results_path)
    
    results += print_final_metrics()
    for key in all_files["transactions"]:
        if "transactions_closed" in key:
            
    # # clear terminal

            final_results += get_client_final_inventary(file_path=f"N:\\TESE\\Bullwhip\\data\\results\\{sim}\\{key}")

# print(results)


print(results)
print(final_results)