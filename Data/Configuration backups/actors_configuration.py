actors= {
    "actors": [
        {
            "Id": 1,
            "Name": "Retalhista",
            "Time_Average": 2,
            "time_deviation": 3,
            "Max_inventory": 60,
            "Reorder_history_days": 7,
            "Products": [
                {
                    "Name": "Cerveja Branca",
                    "id": 1001,
                    "initial_stock": 1000,
                    "safety_stock": 200,
                    "Composition": 2
                },
                {
                    "Name": "Cerveja Preta",
                    "id": 1002,
                    "initial_stock": 1000,
                    "safety_stock": 200,
                    "precedence": [
                        2
                    ]
                },
                {
                    "Name": "Cidra",
                    "id": 1003,
                    "initial_stock": 1000,
                    "safety_stock": 200,
                    "precedence": [
                        2
                    ]
                },
                {
                    "Name": "Garrafa de vinho",
                    "id": 1004,
                    "initial_stock": 200,
                    "safety_stock": 50,
                    "precedence": [
                        12
                    ]
                }
            ]
        },
        {
            "Id": 2,
            "Name": "Distribuidor",
            "Time_Average": 2,
            "time_deviation": 3,
            "Max_inventory": 60,
            "Reorder_history_days": 7,
            "Products": [
                {
                    "Name": "Palete de Cerveja Branca",
                    "id": 2001,
                    "initial_stock": 10,
                    "safety_stock": 4,
                    "precedence": [
                        3
                    ]
                },
                {
                    "Name": "Palete de Cerveja Preta",
                    "id": 2002,
                    "initial_stock": 10,
                    "safety_stock": 4,
                    "precedence": [
                        3
                    ]
                },
                {
                    "Name": "Palete de Cidra",
                    "id": 2003,
                    "initial_stock": 10,
                    "safety_stock": 4,
                    "precedence": [
                        9
                    ]
                }
            ]
        },
        {
            "Id": 3,
            "Name": "Fábrica de Cerveja",
            "Time_Average": 2,
            "time_deviation": 3,
            "Max_inventory": 60,
            "Reorder_history_days": 7,
            "Products": [
                {
                    "Name": "Palete de Cerveja Branca",
                    "id": 3001,
                    "initial_stock": 15,
                    "safety_stock": 5,
                    "precedence": [
                        4,
                        5,
                        6,
                        8
                    ]
                },
                {
                    "Name": "Palete de Cerveja Preta",
                    "id": 3002,
                    "initial_stock": 15,
                    "safety_stock": 5,
                    "precedence": [
                        4,
                        5,
                        6,
                        8
                    ]
                }
            ]
        },
        {
            "Id": 4,
            "Name": "Fábrica de Malte",
            "Time_Average": 2,
            "time_deviation": 3,
            "Max_inventory": 60,
            "Reorder_history_days": 7,
            "Products": [
                {
                    "Name": "Tonelada de Malte",
                    "id": 4001,
                    "initial_stock": 5,
                    "safety_stock": 2,
                    "precedence": [
                        7
                    ]
                }
            ]
        },
        {
            "Id": 5,
            "Name": "Fornecedor de Lupulo",
            "Time_Average": 2,
            "time_deviation": 3,
            "Max_inventory": 60,
            "Reorder_history_days": 7,
            "Products": [
                {
                    "Name": "Saco de Lupulo",
                    "id": 5001,
                    "initial_stock": 5,
                    "safety_stock": 1
                }
            ]
        },
        {
            "Id": 6,
            "Name": "Fornecedor de levedura",
            "Time_Average": 2,
            "time_deviation": 3,
            "Max_inventory": 60,
            "Reorder_history_days": 7,
            "Products": [
                {
                    "Name": "Saco de levedura",
                    "id": 6001,
                    "initial_stock": 15,
                    "safety_stock": 4
                }
            ]
        },
        {
            "Id": 7,
            "Name": "Fornecedor de Cevada",
            "Time_Average": 2,
            "time_deviation": 3,
            "Max_inventory": 60,
            "Reorder_history_days": 7,
            "Products": [
                {
                    "Name": "Tonelada de Cevada",
                    "id": 1001,
                    "initial_stock": 15,
                    "safety_stock": 4
                }
            ]
        },
        {
            "Id": 8,
            "Name": "Fornecedor de Garrafas",
            "Time_Average": 2,
            "time_deviation": 3,
            "Max_inventory": 60,
            "Reorder_history_days": 7,
            "Products": [
                {
                    "Name": "Palete de Garrafas",
                    "id": 8001,
                    "initial_stock": 15,
                    "safety_stock": 4,
                    "precedence": [
                        2
                    ]
                }
            ]
        },
        {
            "Id": 9,
            "Name": "Fábrica de Cidra",
            "Time_Average": 2,
            "time_deviation": 3,
            "Max_inventory": 60,
            "Reorder_history_days": 7,
            "Products": [
                {
                    "Name": "Cidra",
                    "id": 9003,
                    "initial_stock": 15,
                    "safety_stock": 4,
                    "precedence": [
                        10,
                        11
                    ]
                }
            ]
        },
        {
            "Id": 10,
            "Name": "Fornecedor de Maças",
            "Time_Average": 2,
            "time_deviation": 3,
            "Max_inventory": 60,
            "Reorder_history_days": 7,
            "Products": [
                {
                    "Name": "Tonelada de maças",
                    "id": 1001,
                    "initial_stock": 15,
                    "safety_stock": 4
                }
            ]
        },
        {
            "Id": 11,
            "Name": "Fornecedor de Açucar",
            "Time_Average": 2,
            "time_deviation": 3,
            "Max_inventory": 60,
            "Reorder_history_days": 7,
            "Products": [
                {
                    "Name": "Tonelada de açucar",
                    "id": 1101,
                    "initial_stock": 15,
                    "safety_stock": 4
                }
            ]
        },
        {
            "Id": 12,
            "Name": "Garrafeira",
            "Time_Average": 2,
            "time_deviation": 3,
            "Max_inventory": 60,
            "Reorder_history_days": 7,
            "Products": [
                {
                    "Name": "Caixa de Garrafas de Vinho Tinto",
                    "Id": 1201,
                    "initial_stock": 15,
                    "safety_stock": 4,
                    "precedence": [
                        13
                    ]
                }
            ]
        },
        {
            "Id": 13,
            "Name": "Adega",
            "Time_Average": 2,
            "time_deviation": 3,
            "Max_inventory": 60,
            "Reorder_history_days": 7,
            "Products": [
                {
                    "Name": "Palete de Garrafas de Vinho Tint",
                    "id": 1301,
                    "initial_stock": 15,
                    "safety_stock": 4
                }
            ]
        }
    ]
}



def Save_Configurations():
    import json, sys, yaml
    with open("actors_configuration.yaml","w") as file:
        file.write(yaml.dump(actors))
    print("actors_configuration.yaml updated!")

Save_Configurations()