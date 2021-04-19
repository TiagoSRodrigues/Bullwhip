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

        log(info_msg="[Created Object] Actor         id="+str(self.id)+" "+self.name)

        #Initializes the ClassOrdersRecord
        #order_record.stock_record()
        try:
            log(debug_msg = "ACTORS    Created actor: "+str(id)+" " + str(name) + " AVG: "+ str(avg) + " VAR: "+ str(var) + 
                " Initial Stock" + str(initial_stock) + " safety_stock " +str(safety_stock) +
                " max_inventory " + str(max_inventory) + " reorder_history_size " + str(reorder_history_size) +
                " Precedence " + str(precedence))
        except:
            log(debug_msg="Error in Actors logging")


    def get_state(self):
        return self.state
    
    def get_inventory(self): 
        print("the length is: ", len(self.inventory))
        return len(self.inventory)

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





