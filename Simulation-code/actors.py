from logging_management import log
log(debug_msg="Started actors.py")
########################################################################################################################
############################################################################################
#       Classe das funções de gestão interna do actor da cadeia de valor                   #
############################################################################################
class actor:
    def __init__(self , id:int , name:str , avg:int ,
        var:int, initial_stock:int, safety_stock:int,
        max_inventory:int, reorder_history_size:int,
        precedence:list, state=None):
        
        ### Constants Properties  ###
        self.id=id
        self.name = name
        self.average_time = avg
        self.variation_time = var
        self.initial_stock = initial_stock 
        self.safety_stock=safety_stock
        self.max_inventory=max_inventory
        self.reorder_history_size=reorder_history_size # nr of days to consider to reeorder
        self.precedence= precedence
       
       
        ### Variable Properties  ######
        self.state="idle"

        
        #Initializes the orders_record
        #order_record.stock_record()
        try:
            log(debug_msg = "Created actor: "+str(id)+" " + str(name) + " AVG: "+ str(avg) + " VAR: "+ str(var) + 
                " Initial Stock" + str(initial_stock) + " safety_stock " +str(safety_stock) +
                " max_inventory " + str(max_inventory) + " reorder_history_size " + str(reorder_history_size) +
                " Precedence " + str(precedence),
                info_msg = "Created actor: "+str(id)+" " + str(name))
        except:
            log(debug_msg="Error in Actors logging")


    def get_state(self):
        return self.state
    
    def get_inventory(self): 
        print("the length is: ", len(self.inventory))
        return len(self.inventory)

    # Adding of element to queue
    # def add_to_inventory(self, element):
    #     self.inventory.append(element)

    # remove of element 
    # def remove_from_inventory(self, element=0):
    #     self.inventory.pop(element)

    # def show_inventory(self):
    #     for el in self.inventory:
    #         print(el)
    #     #    box=self.inventory.get

    def receive_order(self):

        stock = self.order_record.get_ordered_products()
        min_stock = self.safety_stock
        if stock <= min_stock:
            pass # place_order()
        else:
            pass #deliver()
        
        print("the safety stock is "+self.safety_stock)

    def check_inventory(self,product=None):
        inventory_size=self.get_inventory_size(self,product)


    def get_actor_precedence(self):
        if len(self.precedence)==1:
            return self.precedence[0]
        else:
            print("Supply chain precedence with erros")
            return ReferenceError





