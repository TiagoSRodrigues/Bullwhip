import logging_management as logs, simulation_configuration as sim_cfg
import numpy as np
logs.log(debug_msg="Started Order_records.py")

############################################################################################
#       Classe dos regitos individuais dos actores                                         #
############################################################################################
class ClassOrdersRecord:
    def __init__(self,actor ):
        self.actor = actor
        self.last_order_id = self.actor * 10**6       #tracks the last product id

        #Status order 0-Received 1-waiting 3-sended
        #Acho que o nome n vai servir para nada,
        # columns = ["Time","Product", "Qty","Client","Order_id","Status"]  
        columns = [-1, -2, -3, -4, -5, -6]  
        self.OrdersRecord = np.array([columns])
        self.OrdersRecord.astype(np.int)

        logs.log(info_msg="[Created Object] Order_record  actor:"+str(self.actor)) 
        

#---------------------------------------------------------------------     
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
            order_record=self.filter_by_product(complete_order_record,product)
        else:
            inventory=complete_order_record
        print("\n inventory size: \n",inventory.shape[0])
        return inventory.shape[0]

    def get_orders_record(self):
        print("\n get inventory: \n",self.OrdersRecord)
        return self.record


# \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ 
    def add_to_orders_record(self, Time, Product, Qty, Client):
        logs.log(debug_msg="[FUNCION] with parameters: time:" + str(Time) + " product: "+ str(Product) + " Qty " + str(Qty) + " Client: "+ str(Client))
        actor_id = self.actor
        
        self.last_order_id = self.last_order_id + 1
        #initial status = 0
        to_add = np.array([[Time, Product, Qty,  Client, self.last_order_id, 0]])

        self.OrdersRecord=np.append(self.OrdersRecord,to_add,axis=0)

        logs.log(debug_msg="[ORDERED ADDED]  Products ordered from"+str(self.actor)+" Parameters "+str(to_add))
        
        with open(sim_cfg.orders_record_file, 'a') as file:
            file.write( str(Time) +","+ str(Product) + "," + str(Qty) + ","+ str(Client)+"," + str(self.last_order_id) + ",0\n")
        
    #check the order id and changes the status
    def set_order_status(self, order_id, status):
        for record in self.OrdersRecord:
            if record[-2] == order_id:
                record[-1] = status


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
        return history

    def get_ordered_products(self,time_interval=None,product=None):
        history=self.get_history(time_interval,product=None)
        logs.log(debug_msg="Ordered products: "+history.shape[0]-1)
        return history.shape[0]-1







