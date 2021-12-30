import pymongo
from pymongo import collection


data=
 "transaction_id":self.transaction_id,
                "deliver_day":deliver_date,
                "sending_day":sending_date,
                "receiver":receiver,
                "sender":sender,
                "product":product,
                "quantity": quantity,
                "delivered": False,
                "recording_time": self.simulation.time
                }
"""class MongoDB:
    def __init__(self):
        """Cria a ligação, 
        Apaga as DB anteriores
        Cria as collections
        """
        self.mongo_client = pymongo.MongoClient("mongodb://localhost:2021/")
        self.simulation_db = self.mongo_client["simulation"]
        self.drop_database()
        self.create_colections()

    def create_colections(self):
        """Colections"""
        self.actors_collection = self.simulation_db["actors"]
        self.transactions_collection = self.simulation_db["transactions"]

    def drop_database(self):
        """elimina as dbs resultantes de simulações anteriores"""
        database_list = self.mongo_client.database_names()
        if 'simulation' in database_list:
            self.mongo_client.drop_database("simulation")

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
            
    def get_all_actor_data(self):
        cursor = self.actors_collection.find({})
        for document in cursor:
            print(document)
            
mg = MongoDB()
mg.check_connection()

mg.add_to_actors_db( [{ "name": "Peter", "address": "Lowstreet 27" }] )
mg.add_to_actors_db( [{ "_id": "A1", "oders": [1,2,3], "inventory": {"1":"2","3":"4"}}, { "name": "Peter", "address": "Lowstreet 27" }] )

print(mg.mongo_client.list_database_names())
mg.get_all_actor_data()

"""

        """bACKUP
        
        class DataBase:
    """Database do projecto
    """
    def __init__(self, simulation):
        self.simulation=simulation
        self.client = redis.Redis(host='localhost', port=2022)
        self.check_connection()
        logs.log(debug_msg=        logs.log(debug_msg="| DB Connected     |"))
           # connect to redis

    def add_to_db(self, key, value):
        """Testa se o valor existe e caso não exista adiciona
        """
        if self.get_value(key) is None:
            self.set_value(key, value)
            print("added")
        else:
            print("já existe", self.get_value(key))

    def get_value(self, key):
        """        retorna valor
        """
        return self.client.get(key)

    def set_value(self, key, value):
        """Define o valor da chave, sem testar se existe
        """
        self.client.set(key, value)
        logs.log(debug_msg="| DataBase         | Set for key"+str(key))
        
    def check_connection(self):
        """check connection"""
        try:
            return self.client.ping()
        except redis.exceptions.ConnectionError :
            return logs.log(debug_msg=        logs.log(debug_msg="| DB DisConnected   |"))
            
        """