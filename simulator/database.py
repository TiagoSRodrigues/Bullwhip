import os
from time import sleep
import pymongo
from inspect import stack
import csv
from . import logging_management as logs
import numpy as np
import pandas as pd
# import docker

class MongoDB:
    def __init__(self, simulation, drop_history=True):
        self.simulation=simulation
        self.log_id=0
        """Cria a ligação,
        Apaga as DB anteriores
        Cria as collections
        """
        logs.log(debug_msg="| Connecting to database Connected!        ")
        self.mongo_client = pymongo.MongoClient("mongodb://localhost:2021/")

        self.check_connection()


        self.simulation_db = self.mongo_client["simulation"]

        self.simulation_history = self.mongo_client["simulation_history"]
        if drop_history:
            self.add_to_db_log(self.mongo_client.drop_database("simulation"))
            # self.drop_database()


        self.sim_actors_collection = self.simulation.actors_collection

        #self.actors_collection = self.simulation_db["actors"]
        """
        self.inventory_collection = self.simulation_db["inventory"]
        """

    def save_stats(self, simulation_id):
        for doc in self.simulation_db["simulation_stats"].find({}):
                self.simulation_history[simulation_id].insert_one(doc)

    # def drop_database(self):
    #     """elimina as dbs resultantes de simulações anteriores"""
    #     database_list = self.mongo_client.database_names()
    #     if 'simulation' in database_list:
    #         self.add_to_db_log(self.mongo_client.drop_database("simulation"))

    """
    transactions
    """

    def add_transaction_to_db(self, transaction_id=int, transaction_data=dict):
        """        adiciona a transação à coleção transactions da db simunation no mongodb
        """
        try:
            transaction_data['_id']=transaction_id
            self.add_to_db_log(
                self.simulation_db["open_transactions"].insert_one(transaction_data)
                )
            return True
        except:
            print( "error on add_transaction_to_db - data:" ,transaction_id, transaction_data)
            return False

    def update_transaction_on_db(self, transaction_id, transaction_info):
        self.simulation_db["closed_transactions"].insert_one(transaction_info)
        # transaction_doc = self.simulation_db["transactions"].find_one({"transaction_id":transaction_id})
        # creation_day= int(transaction_doc["sending_day"])
        # order_criation_date=int(transaction_doc["order_criation_day"])
        # today=self.simulation.time
        # transit_time= today - creation_day
        # lead_time=today - order_criation_date
        # #print("\ndelay time",delay_time,type(delay_time),"\n")
        # try:
        #     #removi o delivered como variável pq o método n faz mais nada, só mete delivered
        #     self.add_to_db_log(
        #         self.simulation_db["transactions"].update_one(
        #             {"_id":transaction_id},{"$set":transaction_info}))
        #     #             "delivered":1,
        #     #                                         "updated_day":today,
        #     #                                         "transit_time":transit_time,
        #     #                                         "lead_time": lead_time

        #     #                                         }}
        #     #         )
        #     # )
        # except:
        #     print("eero", transaction_info)

        #     self.add_to_db_log(
        #         self.simulation_db["transactions"].update_one(
        #             {"_id":transaction_id},{"$set":{"delivered":1,
        #                                             "updated_day":today,
        #                                             "transit_time":transit_time,
        #                                             "lead_time": lead_time
        #                                             }}
        #             )
        #     )

    """
    orders
    """

    def add_order_to_db(self,actor_id, time,  product, quantity, client, order_id, status):
        logs.log(debug_msg="| Database         | add order     | Order{} added to {} of qty {} of Product:{} ordered from:{} at time {}".format(order_id, actor_id, quantity, product, client, time ))

        """        adiciona a order à coleção orders da db simunation no mongodb
        """
        data = {"_id": order_id,
                "actor_id": actor_id,
                "order_time": time,
                "product": product,
                "quantity": quantity,
                "client": client,
                "status": status}

        collection_name="orders_"+str(actor_id)
        self.add_to_db_log(
            self.simulation_db[collection_name].insert_one(data)
            )

    def close_order_on_db(self, actor_id, order_id):
        order_colection="orders_"+str(actor_id)
            #removi o delivered como variável pq o método n faz mais nada, só mete delivered
        self.add_to_db_log(
            self.simulation_db[order_colection].update_one(
                {"_id":order_id},{"$set":{"status":1, "close_time":self.simulation.time}}
                )
        )

    def get_actor_orders(self, actor_id):
        collection_name="orders_"+str(actor_id)
        self.simulation_db[collection_name].find()



    """
    INVENTORY
    """
    def add_to_inventory_snapshot(self):
        logs.log(debug_msg="| Database         |add_to_inventory_snapshot | Order"  )

        inventory_dic={"_id": str(self.simulation.time),"inventory":{}}

        for actor in self.sim_actors_collection:
            # print(actor.actor_inventory.main_inventory)
            actor_inv= {}
            for key, value in actor.actor_inventory.main_inventory.items():
                # if type(value)== type(np.int32()):value=int(value)

                if isinstance( value, dict):
                    value_dict={}
                    for sub_key, sub_value in value.items():
                        # print(sub_value, type ( sub_value))
                        # if type(sub_value)== type(np.int32()): value=int(sub_value)
                        if isinstance( sub_value, dict):
                            pass

            actor_inv[str(key)] = value

            # del actor_inv[str(key)]["composition"]
            # print(actor_inv)

            inventory_dic["inventory"][str(actor.id)]=actor_inv
        self.simulation_db["inventory_snapshot"].insert_one(inventory_dic )


    def update_inventory_db(self,actor_id, product, quantity):
        #logs.log(debug_msg="| Database         |add to inventory| Order{} added to {} of qty {} of Product:{} ordered from:{} at time {}".format(order_id, actor_id, quantity, product, client, time ))

        """        adiciona a order à coleção orders da db simunation no mongodb
        """
        collection_name="inventory_"+str(actor_id)

        #inventory_log
        self.simulation_db["inventory_log"].insert_one(
                    {"actor_id":actor_id, "product": product,"quantity":quantity, "last_update":self.simulation.time}
                )

        # print(collection_name)
        doc= self.get_document_by_id(collection_name, product)

        if  (doc is None) or (doc is False):
            # print("false?",doc)
            self.add_to_db_log(
                self.simulation_db[collection_name].insert_one(
                    {"_id":product,"quantity":quantity, "last_update":self.simulation.time}
                )
            )

        else:
            self.add_to_db_log(
                self.simulation_db[collection_name].update_one(
                    {"_id":product},{"$set":{"quantity":quantity, "last_update":self.simulation.time}}
                )
            )
            # print("true?")

    def add_actor_to_db(self, actor_id, orders, inventory):
        data={"id":"A"+str(actor_id),
            "orders":[],
            "inventory":{}}

        self.add_to_db_log(
            self.actors_collection.insert_many(data)
        )

    def check_connection(self):
        """check connection"""
        try:
            self.mongo_client.server_info()
            logs.log(debug_msg="| Database Connected! ")

        except:
            logs.log(debug_msg="| ERROR on database Conection!!!       ")
            print("Error on MongoDB connection ")
            print(" START THE DOCKER CONTAINER!!!")




    def get_document_by_id(self, doc_collection, doc_id):
        self.add_to_db_log("get document from {} with id:{}".format(doc_collection, doc_id))
        doc = self.simulation_db[str(doc_collection)].find_one({"_id":doc_id})

        #print("get",doc_collection,type(doc),doc)
        if isinstance(doc, dict):
            return doc
        else:
            return False

    def add_to_db_log(self, response):
        "esta função grava as ações na db, não mexer"
        self.log_id= self.log_id+1
        data={"_id":self.log_id,
              "action":stack()[1][3],
              "response":str(response)}
        self.simulation_db["db_log"].insert_one(data)



    def create_db_stats_document(self, simulation_id):
        fist_data={"_id":simulation_id,
                    "simulation_id":simulation_id   }
        self.simulation_db["simulation_stats"].insert_one(fist_data)


    def add_simulation_stats_to_db(self,  stat_value):
        self.simulation_db["simulation_stats"].insert_one({"_id":"simulation_stats","stats":stat_value})

    def add_actors_to_db_stats(self, data):
        self.simulation_db["simulation_stats"].insert_one({"_id":"active_actors","active_actors":data})


    def add_to_db_actor_stats(self, stat_name, stat_value):
        data={"_id":stat_name,
              "stats":stat_value.to_dict()}
        self.simulation_db["simulation_stats"].insert_one(data)

    def add_to_actor_delivered_transactions(self, actor_id, transactions):
        data={"_id":"actor_"+str(actor_id),
              "stats":transactions}
        self.simulation_db["delivered_transactions"].insert_one(data)


    def add_runtime_to_stats_db(self,values):
        data={"_id":"runtime",
              "stats":values}
        self.simulation_db["simulation_stats"].insert_one(data)

    def add_open_itens(self,values):
        self.simulation_db["simulation_stats"].insert_one(values)


        # if isinstance(stat_value, pd.DataFrame):
        #     print(stat_value)
        #     self.simulation_db["simulation_stats"].find_one_and_update(
        #         {"_id":simulation_id},
        #         {"$inc":{ "stats":{"$set":{ stat_value.to_dict("dict")}}
        #                  }
        #          }
                # )

        # elif isinstance(stat_value, list):
        #     pass
        #     stat_value=tuple(stat_value)

        # elif isinstance(stat_value, dict):
        #     pass
        #     print(stat_name,stat_value)

        #     # stat_value=tuple(stat_value)
        #     self.simulation_db["simulation_stats"].update_one(
        #         {"_id":simulation_id},{"$set":{ stat_value.to_dict("dict")}}
        #         )


        # # elif self.simulation_db["simulation_stats"].find_one({"_id":simulation_id})  is None:
        # #     fist_data={"_id":simulation_id,
        # #             stat_name:stat_value}
        # #     self.simulation_db["simulation_stats"].insert_one(fist_data)


        # else:
        #     pass
        #     print("else:",type(stat_value), stat_name, stat_value)
        #     data={stat_name,stat_value}
        #     self.simulation_db["simulation_stats"].update_one(
        #         {"_id":simulation_id},{"$set":{ stat_name:stat_value }}
        #         )

    def add_to_db_stats_log(self, stat_value):
        data=stat_value
        self.simulation_db["db_stats_log"].insert_one(data)

    def add_to_db(self, colection_name, data):
        self.simulation_db[colection_name].insert_one(data)

    def add_maney_to_db(self, colection_name, data):
        self.simulation_db[colection_name].insert_many(data)

    def export_db(self, FINAL_EXPORT_FILES_PATH):
        collections = self.simulation_db.list_collection_names()

        for collection in collections:
            df = pd.DataFrame(list(self.simulation_db[collection].find()))
            df.to_csv( FINAL_EXPORT_FILES_PATH + collection + ".csv", index=False)



    """ STATS"""
    def get_collection_data(self, collection_name):
        data=self.simulation_db[collection_name].find()
        for el in data:
            print(el)

    def get_inventories(self):
        main_inventory={}
        re_filter = {"name": {"$regex": r"^inventory_[0-9].*"}}
        collections_list =self.simulation_db.list_collection_names(filter=re_filter)

        for col in collections_list:
            cursor= self.simulation_db[col].find()
            data=[]
            for el in cursor:
                data.append(el)
            main_inventory[col]=[data]
        return main_inventory

    def get_actor_inventory(self, actor_id):
        main_inventory={}
        re_filter = {"name": {"$regex": r"^inventory_"+str(actor_id)+".*"}}
        collections_list =self.simulation_db.list_collection_names(filter=re_filter)

        for col in collections_list:
            cursor= self.simulation_db[col].find()
            data=[]
            for el in cursor:
                data.append(el)
            main_inventory[col]=[data]
        return main_inventory

    def get_transactions(self):
        main_inventory={}
        re_filter = {"name": {"$regex": r"^transactions"}}
        collections_list =self.simulation_db.list_collection_names(filter=re_filter)

        for col in collections_list:
            cursor= self.simulation_db[col].find()
            data=[]
            for el in cursor:
                data.append(el)
            main_inventory[col]=[data]
        return main_inventory

    def get_orders(self):
        main_inventory={}
        re_filter = {"name": {"$regex": r"^orders_[0-9].*"}}
        collections_list =self.simulation_db.list_collection_names(filter=re_filter)

        for col in collections_list:
            cursor= self.simulation_db[col].find()
            data=[]
            for el in cursor:
                data.append(el)
            main_inventory[col]=[data]
        return main_inventory

    def get_actor_orders(self, actor_id):
        orders={}
        re_filter = {"name": {"$regex": r"^orders_"+str(actor_id)+".*"}}
        collections_list =self.simulation_db.list_collection_names(filter=re_filter)

        for col in collections_list:
            cursor= self.simulation_db[col].find()
            data=[]
            for element in cursor:
                data.append(element)
            orders[col]=[data]
        return orders

    def get_simulation_stats(self):
        stats={}
        re_filter = {"name": {"$regex": r"^simulation_stats"}}
        collections_list =self.simulation_db.list_collection_names(filter=re_filter)

        for col in collections_list:
            cursor= self.simulation_db[col].find()
            data=[]
            for el in cursor:
                data.append(el)
            stats[col]=[data]
        return stats

