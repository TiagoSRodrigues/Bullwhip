actors= {
   "Actors":[
      {
         "Id":1,
         "Name":"Retailer",
         "Time_Average":1,
         "Time_variance":1,
         "Max_inventory":60,
         "Reorder_history_size":7,
         "Products":[
            {
               "Name":"ProductA",
               "id":1001,
               "initial_stock":10,
               "safety_stock":2,
               "Composition":{
                  "2001":1
               }
            }, {
               "Name":"ProductAB",
               "id":1001,
               "initial_stock":100,
               "safety_stock":2,
               "Composition":{
                  "2001":12,
                  "1001":100
               }
            }
         ]
      },
      {
         "Id":2,
         "Name":"Distributor",
         "Time_Average":1,
         "Time_variance":1,
         "Max_inventory":60,
         "Reorder_history_size":7,
         "Products":[
            {
               "Name":"ProductB",
               "id":2001,
               "initial_stock":10,
               "safety_stock":4,
               "Composition":{
                  "3001":1
               }
            }
         ]
      },
      {
         "Id":3,
         "Name":"Factory",
         "Time_Average":1,
         "Time_variance":1,
         "Max_inventory":60,
         "Reorder_history_size":7,
         "Products":[
            {
               "Name":"ProductC",
               "id":3001,
               "initial_stock":15,
               "safety_stock":5,
               "Composition":{
                  "4001":1
               }
            }
         ]
      },
      {
         "Id":4,
         "Name":"Raw Material Supplier",
         "Time_Average":1,
         "Time_variance":1,
         "Max_inventory":60,
         "Reorder_history_size":7,
         "Products":[
            {
               "Name":"ProductD",
               "id":4001,
               "initial_stock":5,
               "safety_stock":2,
               "Composition":{
                  "5001":1
               }
            }
         ]
      },
      {
         "Id":5,
         "Name":"Base Raw Material supplier",
         "Time_Average":1,
         "Time_variance":1,
         "Max_inventory":60,
         "Reorder_history_size":7,
         "Products":[
            {
               "Name":"ProductE",
               "id":5001,
               "initial_stock":5,
               "safety_stock":1
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