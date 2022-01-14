
from . import database
import pandas as pd

class calculate_simulations_stats():
    def __init__(self, simulation) -> None:
        self.simulation=simulation
        self.db_connection = database.MongoDB( self.simulation,drop_history=False)
    
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
        actors_collection=self.simulation.actors_collection
        for actor in actors_collection:
            self.db_connection.add_to_db_actor_stats(
                stat_name="actor_"+str(actor.id),
                stat_value=self.get_actor_stats(actor_id=actor.id))
            #print(self.get_actor_stats(actor_id=actor.id).to_json())
            #self.add_to_db_stats

    def add_open_itens_to_db(self, simulation):
        open_transactions = simulation.ObejctTransationsRecords.open_transactions
        open_orders = {}
        for actor in simulation.actors_collection:
            open_orders[actor.id] = actor.actor_orders_record.Open_Orders_Record
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