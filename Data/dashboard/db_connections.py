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