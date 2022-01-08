import db_connections
import pandas as pd

mongo = db_connections.db_connection()

def get_actor_inventory_df(actor_id):
    data=mongo.get_actor_inventory(actor_id)
    return pd.DataFrame(data["inventory_"+str(actor_id)][0])
    
def get_actor_orders_df(actor_id):
    data=mongo.get_actor_orders(actor_id)
    return pd.DataFrame(data["orders_"+str(actor_id)][0])

def get_transactions_df():
    data=mongo.get_transactions()
    return pd.DataFrame(data["transactions"][0],
                        columns=["transaction_id",
                                            "deliver_day",
                                            "order_id",
                                            "sending_day",
                                            "receiver",
                                            "sender",
                                            "product",
                                            "quantity",
                                            "delivered",
                                            "last_update",
                                            "recording_time"])


def update_inventory_data():
    actors=mongo.get_actors_id()
    
    dfs={}
    for actor in actors:
        dfs[actor]=(get_actor_inventory_df(actor))
    return dfs


def get_collection_data(self, collection_name):
    data=self.simulation_db[collection_name].find()
    for el in data:
        print(el)

#print(update_inventory_data())