from . import logging_management as logs
import datetime

class ClassSupplyChain:
    def __init__(self):
        self.supply_chain_structure = []
        self.supply_chain_id="sc_"+str(datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))   

        logs.log(info_msg="[Created Object] Supply chain  id:"+str(self.supply_chain_id)) 

    def add_to_supply_chain(self,actor):
        self.supply_chain_structure.append(actor)
        logs.log(debug_msg=str(actor)+"[Function add_to_supply_chain] chain")
        
    def show_supply_chain(self):
        print(self.supply_chain_structure)
        
    def get_supply_chain(self):
        return self.supply_chain_structure


