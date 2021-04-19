import logging_management as logs
# Funções para correr a simulação, o pré simulação fica no init


def main(input_data, simulation):
    for el in input_data:
        place_main_order(el, simulation)

    ########### Start orders
    simulation.record_simulation_status(simulation_status=3)
    logs.show_object_attributes(simulation)


def place_main_order(number, Object_Simulation):
    number, Object_Simulation = number, Object_Simulation
    pass

