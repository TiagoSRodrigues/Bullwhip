actors= {
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


def Save_Configurations(actors):
    import json, sys, yaml,  time
    import simulation_configuration  as sim_cfg

    with open(sim_cfg.actors_configuration_file,"w") as file:
        file.write(yaml.dump(actors))

    with open(sim_cfg.Configuration_backups+time.strftime("actors_configuration_file "+"%Y%m%d_%H-%M-%S"+".json", time.localtime()),"w") as fp:
        fp.write(json.dumps(actors,indent=4, sort_keys=True))
        
    print("actors_configuration.yaml updated!")

Save_Configurations(actors)


#Todo: adicionar uma função para verificar se os ids n se repetem