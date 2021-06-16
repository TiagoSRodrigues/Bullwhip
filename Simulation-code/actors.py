import  orders_records, inventory, simulation ,logging_management as logs
logs.log(debug_msg="Started actors.py")

############################################################################################
#       Classe das funções de gestão interna do actor da cadeia de valor                   #
############################################################################################
class actor:
    def __init__(self , simulation_object , id:int , name:str , avg:int , var:int, max_inventory:int, reorder_history_size:int,
        products:dict, state=None):
        
        ### Constants Properties  ###
        self.id                   = id
        self.name                 = name
        self.average_time         = avg
        self.variation_time       = var
        self.max_inventory        = max_inventory
        self.reorder_history_size = reorder_history_size # nr of days to consider to reeorder
        self.products             = products
       
        ### Variable Properties  ######
        self.state="idle"

        #Cria o Registo de encomendas
        self.actor_stock_record = orders_records.ClassOrdersRecord(name)
            
        #Cria os inventários                                   #   ↓ Produt is forced to 1   !  this is commented becouse is the crations
        self.actor_inventory = inventory.ClassInventory( actor = name , #product = 1,
                                                    max_capacity = max_inventory,
                                                    products=products)


        logs.log(info_msg="[Created Object] Actor         id="+str(self.id)+" "+self.name)


        #LAST THING: Adiciona o ator à lista de objectos (atores) da simulação
        simulation_object.actors_collection.append(self)

        #logs
        try:
            logs.log(debug_msg = "ACTORS    Created actor: "+str(id)+" " + str(name) + " AVG: "+ str(avg) + " VAR: "+ str(var) + 
                " Initial Stock" + str(initial_stock) + " safety_stock " +str(safety_stock) +
                " max_inventory " + str(max_inventory) + " reorder_history_size " + str(reorder_history_size) +
                " Precedence " + str(precedence))
        except:
            logs.log(debug_msg="Error in Actors logging")
#-------------------------------------------------------------------------------------------------------------------------#

    def get_state(self):
        return self.state
    

    def receive_order(self, quantity, product ):
        self.state = "BUSY"

        in_inventory = self.actor_inventory.check_product_inventory(product)
        in_inventory = self.check_inventory( product = product )
        
        print("there are",in_inventory,"avaiable")

        min_stock = self.safety_stock
        if stock <= min_stock:
            pass # place_order()
        else:
            pass #deliver()
        
        print("the safety stock is "+self.safety_stock)

    def check_inventory(self,product):
        return self.actor_inventory.get_inventory_size(self,product)


    def get_actor_precedence(self):
        if len(self.precedence)==1:
            return self.precedence[0]
        else:
            print("Supply chain precedence with erros")
            return ReferenceError





