
import os

from simulator.logging_management import save_to_file
from . import database
import pandas as pd
import simulation_configuration as sim_cfg
class calculate_simulations_stats():
    def __init__(self, simulation) -> None:
        self.simulation=simulation
        if sim_cfg.DB_TYPE == 1:
            self.db_connection = database.MongoDB(self.simulation,drop_history=False)

        self.calculate_actors_stats()

    def get_actor_inventory_df(self, actor_id):
        data=self.db_connection.get_actor_inventory(1)
        return pd.DataFrame(data["inventory_"+str(1)][0])

    def get_actor_orders_df(self, actor_id):
        data=self.db_connection.get_actor_orders(actor_id)
        return pd.DataFrame(data["orders_"+str(actor_id)][0])

    def get_transactions_df(self):
        data=self.db_connection.get_transactions()
        return pd.DataFrame(self.db_connection.get_transactions()["transactions"][0])

    def get_simulation_stats(self):
        stats=self.db_connection.get_simulation_stats()
        return pd.DataFrame(stats["simulation_stats"][0])

    def get_actor_stats(self,actor_id):
        transactions = self.get_transactions_df()
        actor_transactions = transactions.loc[transactions['receiver'] == actor_id]
        return actor_transactions[["lead_time"]].describe()

    def calculate_actors_stats(self):
        pass
        # actors_collection=self.simulation.actors_collection
        # for actor in actors_collection:
        #     self.db_connection.add_to_db_actor_stats(
        #         stat_name="actor_"+str(actor.id),
        #         stat_value=self.get_actor_stats(actor_id=actor.id))
        #     #print(self.get_actor_stats(actor_id=actor.id).to_json())
            #self.add_to_db_stats

    def add_open_itens_to_db(self, simulation):
        open_transactions = simulation.ObejctTransationsRecords.open_transactions
        open_orders = {}
        for actor in simulation.actors_collection:
            open_orders[actor.id] = actor.actor_orders_record.open_orders_record
        save_data={"_id":"open_itens",
                   "data":
            {
            "open_transactions":tuple(open_transactions),
                   "open_orders":str(open_orders)
                   }
        }
        self.db_connection.add_open_itens(save_data)

    def add_delivered_transactions_to_td(self, simulation):
        for actor in simulation.actors_collection:
            transactions_list = actor.received_transactions

            self.db_connection.add_to_actor_delivered_transactions(actor_id= actor.id, transactions = transactions_list)
    
    def extract_results(self, file_name=None):
        # RESULTS_PATH  
        def read_inventory_file(file_path):
            with open(file_path, "r") as file:
                data = file.read()
                data= data.replace("'",'"')[:-2].replace("\n",'').replace(" ",'')
                
                data = '{"data":[' + data + ']}'
                return data


        files_in_folder = os.listdir(self.simulation.simulation_results_folder)
        string1 = "  Final results exports  "

        # validation parameters
        has_transactions = False
        has_inventory = False
        has_transactions = False
        
        for file in files_in_folder:
            if "transactions_closed" in file:
                has_transactions = True
                trans_data=read_inventory_file((self.simulation.simulation_results_folder + file))
                transactions = pd.read_json(trans_data, orient="split")
                transactions.sort_values(by=["deliver_day", "receiver"], inplace=True)
                transactions.index = transactions["transaction_id"]

        
        if has_transactions:
            string1 += "\n|-------> Transações\n"
            string1 += f"Lead Time - média: {transactions[['lead_time']].mean()[0]:,.{0}f} dias\n".replace(',', ' ')
            string1 += f"Lead Time - std: {transactions[['lead_time']].std()[0]:,.{0}f} dias\n".replace(',', ' ')
            string1 += f"Quantidade encomendada - avg: {transactions[['quantity']].mean()[0]:,.{0}f} unidades\n".replace(',', ' ')
            string1 += f"Quantidade encomendada - std: {transactions[['quantity']].std()[0]:,.{0}f} unidades \n".replace(',', ' ')
            string1 += f"Quantidade encomendada - min: {transactions[['quantity']].min()[0]:,.{0}f} unidades \n".replace(',', ' ')
            string1 += f"Quantidade encomendada - max: {transactions[['quantity']].max()[0]:,.{0}f} unidades \n".replace(',', ' ')
            string1 += f"Quantidade encomendada total: {transactions[['quantity']].sum()[0]:,.{0}f} unidades \n".replace(',', ' ')



        inventory_files = {} 
        i=0
        for file in files_in_folder:
            if "inventory" in file:
                if "actor_" in file:
                    inventory_files[f"actor_{i}"] = file
                    i+=1
                    has_inventory = True
        
                        


        inventories={}
        for actor, inv in inventory_files.items():
            inicial_data = read_inventory_file(self.simulation.simulation_results_folder + inventory_files[actor])
            inventories[actor] = pd.read_json(inicial_data, orient="split")
            inventories[actor] = pd.concat([inventories[actor].drop(['inventory'], axis=1), inventories[actor]['inventory'].apply(pd.Series)], axis=1)







        string1=string1+"|-------> Inventários "
        for actor, inv in inventories.items():
            for col in inventories[actor].columns:
                if col != "day":
                    # print("a", actor, "c", col, "d",  inventories[actor])
                    string1 += f"{actor} {col} -média: {inventories[actor][col].mean():,.{0}f} unidades \n".replace(',', ' ')
                    string1 += f"{actor} {col} -máximo: {inventories[actor][col].max():,.{0}f} unidades \n".replace(',', ' ')
                    string1 += f"{actor} {col} -mínimo: {inventories[actor][col].min():,.{0}f} unidades \n".replace(',', ' ')
                    string1 += f"{actor} {col} -desvio padrão: {inventories[actor][col].std():,.{0}f} unidades \n".replace(',', ' ')
                    string1 += f"{actor} {col} -total: {inventories[actor][col].sum():,.{0}f} unidades\n".replace(',', ' ')
        
        
        
        
        if file_name:
            save_to_file(file_name = self.simulation.simulation_results_folder +file_name, data=string1 )
        
        

    def save_final_stats_on_db(Object_Simulation, final_time):
            Object_Simulation.add_open_itens_to_db(Object_Simulation)
            Object_Simulation.add_delivered_transactions_to_td(Object_Simulation)
            Object_Simulation.db_connection.add_runtime_to_stats_db(round(final_time, 2) )
            Object_Simulation.db_connection.add_simulation_stats_to_db(stat_value= Object_Simulation.simulation_stats)
            Object_Simulation.db_connection.save_stats(Object_Simulation.simulation_id)
            Object_Simulation.db_connection.export_db(self.simulation.simulation_results_folder)

