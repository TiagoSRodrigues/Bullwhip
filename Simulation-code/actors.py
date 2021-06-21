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
        self.actor_stock_record = orders_records.ClassOrdersRecord(self.id)

            
        #Cria os inventários                                   #   ↓ Produt is forced to 1   !  this is commented becouse is the crations
        self.actor_inventory = inventory.ClassInventory( actor = name , #product = 1,
                                                    max_capacity = max_inventory,
                                                    products=products)


        logs.log(info_msg="[Created Object] Actor         id="+str(self.id)+" "+self.name)


        #LAST THING: Adiciona o ator à lista de objectos (atores) da simulação
        simulation_object.actors_collection.append(self)

        #logs
        try:
            logs.log(debug_msg = "ACTORS    Created actor: "+str(self.id)+" " + str(self.name) + " AVG: "+ str(self.average_time) + " VAR: "+ str(self.variation_time) + 
                " max_inventory " + str(self.max_inventory) + " reorder_history_size " + str(self.reorder_history_size) +
                " Products " + str(self.products) )
        except:
            logs.log(debug_msg = "Error in Actors logging")
#-------------------------------------------------------------------------------------------------------------------------#

    def get_state(self):
        return self.state
    

    def receive_order(self, ordered_quantity, product ):
        logs.log(debug_msg = "[Ordered recived] from:"+ str(self.id) + "received an order of "+ str(ordered_quantity) + "of the product" + str(product) )
        self.state = "BUSY"
        
        # in_inventory = self.actor_inventory.get_product_inventory(product)       #[APAGAR
       
        #print("The product " , product , " has " , in_inventory ,  " in stock")   #[APAGAR]

        print( self.Object_Simulation.time)
        self.actor_stock_record.add_to_orders_record( self.time, "Product", "Qty", "Client")



        #AQUI adicionar as variaveis para a order
 
        

    def check_inventory(self,product):
        return self.actor_inventory.get_inventory_size(self,product)



