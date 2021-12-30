"""documentação redis:
https://redis.io/commands
"""
import re
from pymongo import collection
import redis
import pymongo
#from pymongo import collection
from . import logging_management as logs

class MongoDB:
    def __init__(self, simulation, drop_history=True):
        self.simulation=simulation
        """Cria a ligação, 
        Apaga as DB anteriores
        Cria as collections
        """
        self.mongo_client = pymongo.MongoClient("mongodb://localhost:2021/")
        self.simulation_db = self.mongo_client["simulation"]
        
        if drop_history:
            self.drop_database()

        """
        self.actors_collection = self.simulation_db["actors"]
        self.inventory_collection = self.simulation_db["inventory"]
        """
    def drop_database(self):
        """elimina as dbs resultantes de simulações anteriores"""
        database_list = self.mongo_client.database_names()
        if 'simulation' in database_list:
            self.mongo_client.drop_database("simulation")

    def add_transaction_to_db(self, transaction_id=int, transaction_data=dict):
        """        adiciona a transação à coleção transactions da db simunation no mongodb
        """
        try:
            transaction_data['_id']=transaction_id
            
            self.simulation_db["transactions"].insert_one(transaction_data)
            return True
        except:
            print( "error on add_transaction_to_db - data:" ,transaction_id, transaction_data)
            return False

    def update_transaction_on_db(self, transaction_id):
        try:
            #removi o delivered como variável pq o método n faz mais nada, só mete delivered
            self.simulation_db["transactions"].update_one({"_id":transaction_id},{"$set":{"delivered":1, "recording_time":self.simulation.time}})
        except:
            self.simulation_db["transactions"].update_one({"_id":transaction_id},{"$set":{"delivered":1, "recording_time":self.simulation.time}})    
        

    def add_order_to_db(self,actor_id, time,  product, quantity, client, order_id, status):
        logs.log(debug_msg="| Database         | add order     | Order{} added to {} of qty {} of Product:{} ordered from:{} at time {}".format(order_id, actor_id, quantity, product, client, time ))

        """        adiciona a order à coleção orders da db simunation no mongodb
        """
        data = {"_id": order_id,
                "actor_id": actor_id,
                "time": time,
                "product": product,
                "quantity": quantity,
                "client": client,
                "status": status}
       
        collection_name="orders_"+str(actor_id)
        self.simulation_db[collection_name].insert_one(data)

    def close_order_on_db(self, actor_id, order_id):
        order_colection="orders_"+str(actor_id)
        try:
            #removi o delivered como variável pq o método n faz mais nada, só mete delivered
            self.simulation_db[order_colection].update_one({"_id":order_id},{"$set":{"status":1, "close_time":self.simulation.time}})
        except:
            self.simulation_db[order_colection].update_one({"_id":order_id},{"$set":{"status":1, "close_time":self.simulation.time}})
            raise Exception("Error closing order on db")
            
        

    # def add_to_simulation_db(self, collection_name, value):
    #     print("size: ",value)
    #     if isinstance(value, dict):
    #         value=[value]
    #         if collection_name == "actors":
    #             self.actors_collection.insert_many(value)
    #         elif collection_name == "inventory":
    #             self.inventory_collection.insert_many(value)
    #         elif collection_name == "transactions":
    #             print("added")
    #             self.transactions_collection.insert_many(value)
    #         elif collection_name == "simulation_engine":
    #             self.simulation_engine.insert_many(value)
    #         else: 
    #             print("ERRO no método add to mongo db")
        
    def add_actor_to_db(self, actor_id, orders, inventory):
        data={"id":"A"+str(actor_id),
            "orders":[],
            "inventory":{}}
     
        self.actors_collection.insert_many(data)
    
    def check_connection(self):
        """check connection"""
        try:
            if self.mongo_client.server_info():
                print("ok")
                return True
        except:
            print("Erro no Mongo DB")
            
    def get_all_collection_data(self, collection):
        if collection == "actors":
            cursor = self.actors_collection.find({})
        elif collection == "inventory":
            cursor = self.inventory_collection.find({})
        elif collection == "transactions":
            cursor = self.transactions_collection.find({})
        else:
            print("ERRO no método get_all_collection_data mongo db")
        
        for document in cursor:
            print(document)
    
def db_tests():
    db = MongoDB("teste")
    db.check_connection()


    db.update_transaction_on_db(1)
    # for i in range(100):
    #     data= {
    #         "deliver_day":i+3,
    #         "sending_day":i,
    #         "receiver":0,
    #         "sender":1,
    #         "product":1000+i,
    #         "quantity": 10+i,
    #         "delivered": 0,
    #         "recording_time": i
    #     }
    #     db.add_transaction(i,data)
        # def set_actor_order(self, actor, order):
        #     value= dd_to_simulation_db(self,collection, value)
    
#db_tests()        
# # mg = MongoDB()
# # mg.check_connection()

# # mg.add_to_simulation_db("actors" ,[{ "name": "Peter", "address": "Lowstreet 27" }] )

# # print(mg.mongo_client.list_database_names())
# # mg.get_all_collection_data("actors")

