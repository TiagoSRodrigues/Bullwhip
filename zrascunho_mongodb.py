import pymongo
mongo_client = pymongo.MongoClient("mongodb://localhost:2021/")

simulation_db = mongo_client["simulation"]
        

def get_collections_on_db():
    collections=[]
    for i in simulation_db.list_collections():
        collections.append( i["name"])
    return collections
        
        

        
# s=(simulation_db["transactions"].find_one({"_id":1}))
# print(type(s))


def get_actor_orders( actor_id):
    collection_name="orders_"+str(actor_id)
    return simulation_db[collection_name].find()
