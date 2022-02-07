from . import logging_management as logs
import datetime



'''
O supply chain tem o objectivo de guardar a estrutura da cadeia, ou seja, 
a ordem das relações entre atores, não informação sobre os elementos

é importante identificar quais os elementos dos estemos das cadeiras para evitar loops infinitos

idealmente isto seria um grafo orientado
'''
class ClassSupplyChain:
    def __init__(self, simulation):
        self.simulation = simulation
        self.supply_chain_structure = []
        self.supply_chain_id="sc_"+str(datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))  
        self.end_of_chain_actors =[] #TODO tinha aqui um 5, verificar se ao remove-lo n estragou nada

        logs.log(info_msg="| CREATED OBJECT   | Supply chain  id:"+str(self.supply_chain_id)) 

    def add_to_supply_chain(self,actor):
        self.supply_chain_structure.append(actor)
        # print("add,",self.supply_chain_structure, self.end_of_chain_actors, self.get_end_of_chain_actors())
        logs.log(debug_msg="| FUNCTION         | supply_chain.add_to_supply_chain"+str(actor))
        
    def show_supply_chain(self):
        print(self.supply_chain_structure)
        
    def get_supply_chain(self):
        return self.supply_chain_structure

    def get_end_of_chain_actors(self):
        return [max(self.supply_chain_structure)]

        #isto não está rubusto apenas funciona para SC lineares 
        #a função devia devolver uma lista dos elementos de fim de cadeia (que devem ter um inventário infinto)


    #todo criar uma função para construir o SC a aprtir da leitura da configuração
    # ciar um grafo a partir da analise da config 