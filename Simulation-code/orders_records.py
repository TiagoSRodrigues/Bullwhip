from logging_management import log
import numpy as np
log(debug_msg="Started Order_records.py")


############################################################################################
#       Classe dos regitos individuais dos actores                                         #
############################################################################################
class ClassOrdersRecord:
    def __init__(self,actor ):
        self.actor = actor
        #Acho que o nome n vai servir para nada,
        # columns = ["Time","Product", "Qty","Client"]  
        columns = [-1, -2,-3, -4 ]  
        self.ClassOrdersRecord = np.array([columns])
        log(info_msg="[Created Object] Order_record  actor:"+str(actor.name)) 
     
    def filter_by_product(self,complete_history,product):
            filter_arr = []
            
            for element in complete_history:
                if element[3] == product:
                    filter_arr.append(True)
                else:
                    filter_arr.append(False)

            filtered = complete_history[filter_arr]
            return filtered

    def get_record_size(self,product=None):
        complete_order_record=self.record
         #Filter by product
        if product != None:
            order_record=self.filter_by_product(complete_inventory,product)
        else:
            inventory=complete_inventory
        print("\n inventory size: \n",inventory.shape[0])
        return inventory.shape[0]

    def get_order_record(self):
        print("\n get inventory: \n",self.record)
        return self.record

    def add_to_record(self, Time, Product, Qty, Client):
        to_add = np.array([[Time, Product, Qty,  Client]])
        self.record=np.append(self.record,to_add,axis=0)
        log(debug_msg=str(to_add)+" products ordered from"+str(self.actor))

    def get_history(self,time_interval=None,product=None):
        print("\n inputs: \n",self,time_interval,product)      
        complete_history=self.record

        #Filter history by product
        if product != None:
            history=self.filter_by_product(complete_history,product)

        elif time_interval == None:
            history=complete_history[:,:]
       
        #filter by date
        elif time_interval != None:
            history=complete_history[-time_interval:,:]
            # print("\n history shape:" ,history.shape)
            # print("\n history: \n" ,history)
        return history

    def get_ordered_products(self,time_interval=None,product=None):
        history=self.get_history(time_interval,product=None)
        log(debug_msg="Ordered products: "+history.shape[0]-1)
        return history.shape[0]-1









# import random
# def r(a,b):
#     return random.randint(a,b)

# a=order_record("A")
# # a.get_order_record()
# a.add_to_record(1,2,3,4)
# a.add_to_record(2,3,4,5)
# a.add_to_record(3,4,5,6)
# a.add_to_record(4,5,6,7)
# a.add_to_record(5,6,7,8)

# for i in range(6,1001,1):
#     a.add_to_record(i,1,r(0,5),r(0,5))
# # a.get_inventory_size()
# # a.get_history(time_interval=30,product=1)
# # print(a.get_history(product=2))
# a.get_inventory_size(3)