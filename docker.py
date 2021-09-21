import pymongo
# client = pymongo.MongoClient("mongodb://localhost:1974/")
client = pymongo.MongoClient("mongodb://127.0.0.1:27017/?compressors=disabled&gssapiServiceName=mongodb")
db = client["Bullship"]
actors_configuration = db["Bullship"]
initial_configuration={
"actors":
    [
     
        {
            "id": 1,
            "name": "Retailer",
            "time_average": 1,
            "time_variance": 1,
            "max_inventory": 1000,
            "products":
            [
                {
                    "name": "ProductA",
                    "id": 1001,
                    "initial_stock": 3,
                    "safety_stock": 2,
                    "reorder_history_size": 7,
                    "composition":
                    {
                        2001: 1,
                    }
                },  {
                    "name": "ProductA",
                    "id": 2001,
                    "initial_stock": 3,
                    "safety_stock": 2,
                    "reorder_history_size": 7,
                    "composition":
                    {
                        3001: 1,
                    }
                },
              
            ]
        },
        {
            "id": 2,
            "name": "Distributor",
            "time_average": 1,
            "time_variance": 1,
            "max_inventory": 1000,
            "products":
            [
                {
                    "name": "ProductB",
                    "id": 2001,
                    "initial_stock": 5,
                    "safety_stock": 2,
                    "reorder_history_size": 7,
                    "composition":
                    {
                        3001: 1
                    }
                }
            ]
        },
        {
            "id": 3,
            "name": "Factory",
            "time_average": 1,
            "time_variance": 1,
            "max_inventory": 600,
            "products":
            [
                {
                    "name": "ProductC",
                    "id": 3001,
                    "initial_stock": 5,
                    "safety_stock": 2,
                    "reorder_history_size": 7,
                    "composition":
                    {
                        4001: 1
                    }
                }
            ]
        },
        {
            "id": 4,
            "name": "Raw Material Supplier",
            "time_average": 1,
            "time_variance": 1,
            "max_inventory": 600,
            "products":
            [
                {
                    "name": "ProductD",
                    "id": 4001,
                    "initial_stock": 5,
                    "safety_stock": 2,
                    "reorder_history_size": 7,
                    "composition":
                    {
                        5001: 1
                    }
                }
            ]
        },
        {
            "id": 5,
            "name": "Base Raw Material supplier",
            "time_average": 1,
            "time_variance": 1,
            "max_inventory": 9999999999,
            "products":
            [
                {
                    "name": "ProductE",
                    "id": 5001,
                    "initial_stock": 99999,
                    "safety_stock": 1,
                    "reorder_history_size": 7
                }
            ]
        }
    ]
    }


# customers_list = [
#   { "name": "Amy", "address": "Apple st 652"},
#   { "name": "Hannah", "address": "Mountain 21"},
#   { "name": "Michael", "address": "Valley 345"},
#   { "name": "Sandy", "address": "Ocean blvd 2"},
#   { "name": "Betty", "address": "Green Grass 1"},
#   { "name": "Richard", "address": "Sky st 331"},
#   { "name": "Susan", "address": "One way 98"},
#   { "name": "Vicky", "address": "Yellow Garden 2"},
#   { "name": "Ben", "address": "Park Lane 38"},
#   { "name": "William", "address": "Central st 954"},
#   { "name": "Chuck", "address": "Main Road 989"},
#   { "name": "Viola", "address": "Sideway 1633"},
# ]
x = actors_configuration.insert_many(initial_configuration)
# print list of the _id values of the inserted d



print(x.inserted_ids)
