import pymongo

class db_connection():
    def __init__(self):

        self.mongo_client = pymongo.MongoClient("mongodb://localhost:2021/")
        self.simulation_db = self.mongo_client["simulation"]

    def get_collection_data(self, collection_name):
        data=self.simulation_db[collection_name].find()
        for el in data:
            print(el)

    def get_inventories(self):
        main_inventory={}
        filter = {"name": {"$regex": r"^inventory_[0-9].*"}}
        collections_list =self.simulation_db.list_collection_names(filter=filter)

        for col in collections_list:
            cursor= self.simulation_db[col].find()
            data=[]
            for el in cursor:
                data.append(el)
            main_inventory[col]=[data]
        return main_inventory

    def get_actor_inventory(self, actor_id):
        main_inventory={}
        query_filter = {"name": {"$regex": r"^inventory_"+str(actor_id)+".*"}}
        collections_list =self.simulation_db.list_collection_names(filter=query_filter)

        for col in collections_list:
            cursor= self.simulation_db[col].find()
            data=[]
            for el in cursor:
                data.append(el)
            main_inventory[col]=[data]
        return main_inventory

    def get_transactions(self):
        main_inventory={}
        query_filter = {"name": {"$regex": r"^transactions"}}
        collections_list =self.simulation_db.list_collection_names(filter=query_filter)

        for col in collections_list:
            cursor= self.simulation_db[col].find()
            data=[]
            for el in cursor:
                data.append(el)
            main_inventory[col]=[data]
        return main_inventory

    def get_orders(self):
        main_inventory={}
        query_filter = {"name": {"$regex": r"^orders_[0-9].*"}}
        collections_list =self.simulation_db.list_collection_names(filter=query_filter)

        for col in collections_list:
            cursor= self.simulation_db[col].find()
            data=[]
            for el in cursor:
                data.append(el)
            main_inventory[col]=[data]
        return main_inventory

    def get_actor_orders(self, actor_id):
        orders={}
        query_filter = {"name": {"$regex": r"^orders_"+str(actor_id)+".*"}}
        collections_list =self.simulation_db.list_collection_names(filter=query_filter)

        for col in collections_list:
            cursor= self.simulation_db[col].find()
            data=[]
            for el in cursor:
                data.append(el)
            orders[col]=[data]
        return orders

    def get_actors_id(self):
        #query_filter = {"name": {"$regex": r"^simulation_stats"}}
        actors_list = self.simulation_db["simulation_stats"].find_one({"_id":"active_actors"})["active_actors"]
        actors_list.sort()
        return actors_list

    # def update_datasets(self):
    #     actors=self.get_actors_id()

    #     #inventories

    #     #orders

    #     #