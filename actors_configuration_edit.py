import json
import time
import simulation_configuration  as sim_cfg

actors= {
    "actors": [
        {
            "id": 1,
            "name": "Retailer",
            "time_average": 5,
            "time_deviation": 1,
            "max_inventory": 100_000_000,
           "safety_factor": 2.33,
            "reorder_history_size": 30,
            "products": [
                {
                    "name": "ProductA",
                    "id": 1001,
                    "initial_stock": 12050,
                    "safety_stock": 12050,
                    "composition": {
                        2001: 1
                    }
                }
            ]
        },
        {
            "id": 2,
            "name": "Distributor",
            "time_average": 5,
            "time_deviation": 1,
            "max_inventory": 100_000_000,
           "safety_factor": 2.33,
            "reorder_history_size": 30,
            "products": [
                {
                    "name": "ProductB",
                    "id": 2001,
                    "initial_stock": 12050,
                    "safety_stock": 12050,
                    "composition": {
                        3001: 1
                    }
                }
            ]
        },
        {
            "id": 3,
            "name": "Factory",
            "time_average": 5,
            "time_deviation": 1,
            "max_inventory": 100_000_000,
           "safety_factor": 2.33,
            "reorder_history_size": 30,
            "products": [
                {
                    "name": "ProductC",
                    "id": 3001,
                    "initial_stock": 12050,
                    "safety_stock": 12050,
                    "composition": {
                        4001: 1
                    }
                }
            ]
        },
        {
            "id": 4,
            "name": "Raw Material Supplier",
            "time_average": 5,
            "time_deviation": 1,
            "max_inventory": 100_000_000,
           "safety_factor": 2.33,
            "reorder_history_size": 30,
            "products": [
                {
                    "name": "ProductD",
                    "id": 4001,
                    "initial_stock": 12050,
                    "safety_stock": 12050,
                    "composition": {
                        5001: 1
                    }
                }
            ]
        },
        {
            "id": 5,
            "name": "Raw Material Supplier",
            "time_average": 5,
            "time_deviation": 1,
            "max_inventory": 100_000_000,
           "safety_factor": 2.33,
            "reorder_history_size": 30,
            "products": [
                {
                    "name": "ProductD",
                    "id": 5001,
                    "initial_stock": 12050,
                    "safety_stock": 12050,
                    "composition": {
                        6001: 1
                    }
                }
            ]
        },
        {
            "id": 6,
            "name": "Raw Material Supplier",
            "time_average": 5,
            "time_deviation": 1,
            "max_inventory": 100_000_000,
           "safety_factor": 2.33,
            "reorder_history_size": 30,
            "products": [
                {
                    "name": "ProductD",
                    "id": 6001,
                    "initial_stock": 12050,
                    "safety_stock": 12050,
                    "composition": {
                        7001: 1
                    }
                }
            ]
        },
        {
            "id": 7,
            "name": "Raw Material Supplier",
            "time_average": 5,
            "time_deviation": 1,
            "max_inventory": 100_000_000,
           "safety_factor": 2.33,
            "reorder_history_size": 30,
            "products": [
                {
                    "name": "ProductD",
                    "id": 7001,
                    "initial_stock": 12050,
                    "safety_stock": 12050,
                    "composition": {
                        8001: 1
                    }
                }
            ]
        },
        {
            "id": 8,
            "name": "Raw Material Supplier",
            "time_average": 5,
            "time_deviation": 1,
            "max_inventory": 100_000_000,
           "safety_factor": 2.33,
            "reorder_history_size": 30,
            "products": [
                {
                    "name": "ProductD",
                    "id": 8001,
                    "initial_stock": 12050,
                    "safety_stock": 12050,
                    "composition": {
                        9001: 1
                    }
                }
            ]
        },
        {
            "id": 9,
            "name": "Base Raw Material supplier",
            "time_average": 5,
            "time_deviation": 1,
            "max_inventory": 9_999_999_999_999_999,
           "safety_factor": 2.33,
            "reorder_history_size": 30,
            "products": [
                {
                    "name": "ProductE",
                    "id": 9001,
                    "initial_stock": 9_999_999_999_999_999,
                    "safety_stock": 999_999_999,
                    "reorder_history_size": 7
                },
            ]
        }
    ]
}


####
# Casos de teste
# A- stock inicial = 0      | safety_factor = 1.33
# B- stock inicial = 100000 | safety_factor = 1.33
# C - stock inicial = 0     | safety_factor = 2.33
# D - stock inicial = 100000| safety_factor = 2.33
#

filename = sim_cfg.ACTORS_CONFIGS_DIRECTORY + "actors_configuration_G.json"

def save_configurations(actors_dict):
    """valida e guarda as configurações"""

    with open(filename,"w", encoding="utf-8") as file:
        file.write(json.dumps(actors_dict))

    with open(sim_cfg.CONFIGS_BACKUP+time.strftime("ACTORS_CONFIG_FILE "+"%Y%m%d_%H-%M-%S"+".json", time.localtime()),"w", encoding="utf-8") as file:
        file.write(json.dumps(actors_dict,indent=4, sort_keys=True))

    print(f"{filename} updated!")

save_configurations(actors)
