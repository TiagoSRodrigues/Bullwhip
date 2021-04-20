import logging_management as logs
# Funções para correr a simulação, o pré simulação fica no init


def main(input_data, simulation):
    last_element=get_last_element(simulation)

    for quantity in input_data:
        place_main_order(last_element, quantity, product=1  )

    ########### Start orders
    simulation.record_simulation_status(simulation_status=3)
   


def place_main_order(last_element, quantity, product):
    last_element.receive_order(quantity , product)
    

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