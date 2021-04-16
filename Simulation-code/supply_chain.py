import logging_management as log
class supply_chain:
    def __init__(self):
        self.supply_chain_structure = []
        log.log(debug_msg="Supply chain crated")
        print("Entrou")

    def add_to_supply_chain(self):
        print("supply_chain_structure:#####################################################")
        # self.supply_chain_structure.append(actor)
        # log.log(debug_msg=str(actor)+"Added to supply chain")
        
    def show_supply_chain(self):
        print(self.supply_chain_structure)
        
    def get_supply_chain(self):
        return self.supply_chain_structure


a=supply_chain()

b=a.add_to_supply_chain()