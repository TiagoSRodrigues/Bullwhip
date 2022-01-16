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


def drop_old_history():
    mydb = mongo_client["simulation_history"]
    collections=[]
    for i in mydb.list_collections():
        col_name=i["name"]
        collections.append( col_name)
        print(int(col_name)<20220116000000)
        if int(col_name) < 20220116000000:
            
            mongo_client["simulation_history"][col_name].drop()
        
    return collections



print(drop_old_history()    )
#mongo_client["simulation_history"]["20220112_222404"].drop()