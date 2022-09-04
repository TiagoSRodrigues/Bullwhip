actors= {
    "actors":
    [
        {
            "id": 1,
            "name": "Retailer",
            "time_average": 10,
            "time_deviation": 3,
            "max_inventory": 1000000,
            "safety_factor": 2.33,
            "reorder_history_size":90,
            "products":
            [
                {
                    "name": "ProductA",
                    "id": 1001,
                    "initial_stock": 13648,
                    "safety_stock": 0,
                    "composition":
                    {
                        2001: 1
                    }
                }

            ]
        },
        {
            "id": 2,
            "name": "Distributor",
            "time_average": 10,
            "time_deviation": 3,
            "max_inventory": 1000000,
            "safety_factor": 2.33,
            "reorder_history_size":90,
            "products":
            [
                {
                    "name": "ProductB",
                    "id": 2001,
                    "initial_stock": 13648,
                    "safety_stock": 0,
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
            "time_average": 10,
            "time_deviation": 3,
            "max_inventory": 1000000,
            "safety_factor": 2.33,
            "reorder_history_size":90,
            "products":
            [
                {
                    "name": "ProductC",
                    "id": 3001,
                    "initial_stock": 13648,
                    "safety_stock": 0,
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
            "time_average": 10,
            "time_deviation": 3,
            "max_inventory": 1000000,
            "safety_factor": 2.33,
            "reorder_history_size":90,
            "products":
            [
                {
                    "name": "ProductD",
                    "id": 4001,
                    "initial_stock": 13648,
                    "safety_stock": 0,
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
            "time_average": 10,
            "time_deviation": 3,
            "max_inventory": 9999999999,
            "safety_factor": 2.33,
            "reorder_history_size":90,
            "products":
            [
                {
                    "name": "ProductE",
                    "id": 5001,
                    "initial_stock": 9999999999,
                    "safety_stock": 1,
                    "reorder_history_size": 7
                }
            ]
        }
    ]
}


def Save_Configurations(actors):
    import json, json,  time
    import simulation_configuration  as sim_cfg

    with open(sim_cfg.ACTORS_CONFIG_FILE,"w") as file:
        file.write(json.dumps(actors))

    with open(sim_cfg.CONFIGS_BACKUP+time.strftime("ACTORS_CONFIG_FILE "+"%Y%m%d_%H-%M-%S"+".json", time.localtime()),"w") as fp:
        fp.write(json.dumps(actors,indent=4, sort_keys=True))

    print("actors_configuration.json updated!")

Save_Configurations(actors)


#Todo: adicionar uma função para verificar se os ids n se repetem