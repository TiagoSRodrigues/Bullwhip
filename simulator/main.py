from.import logging_management as logs
# Funções para correr a simulação, o pré simulação fica no init
import time

def main(input_data, simulation):
    logs.log(info_msg="[Function Call] main.main")
    
    
    last_element = get_last_element(simulation)

    for quantity in input_data:
        print("day ",simulation.time)

        last_element.receive_order(quantity = quantity, product=1001, client = 0  )
        simulation.dashboard.update_datasets()
        ## INCREASE TIME
        time.sleep(0.5)
        simulation.time += 1

    ########### Start orders
    simulation.record_simulation_status(simulation_status=3)
    
    
def get_all_elements(simulation):
    return simulation.Object_supply_chain.get_supply_chain()

def get_last_element(simulation):
    last_sc_element_id=simulation.Object_supply_chain.get_supply_chain()[0]
        
    for actor in simulation.actors_collection:
        if actor.id == last_sc_element_id:
            Last_Object=actor
    return Last_Object




# print(simulation.actors_collection[0].name)
"""    try: 
        logs.show_object_attributes(logs.show_object_attributes(simulation))
    except:
        print("Nop")
        logs.show_object_attributes(simulation)
        """