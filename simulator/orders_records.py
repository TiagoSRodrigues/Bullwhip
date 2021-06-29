from . import logging_management as logs
import simulation_configuration as sim_cfg
import numpy as np
logs.log(debug_msg="Started Order_records.py")

############################################################################################
#       Classe dos regitos individuais dos actores                                         #
############################################################################################
class ClassOrdersRecord:
    def __init__(self,actor ):
        self.actor = actor
        self.last_order_id = self.actor.id * 10**6       #tracks the last product id

        #Status order 0-Received 1-sended
        #Acho que o nome n vai servir para nada,
        # columns = ["Time", "Product", "Qty","Client","Order_id","Status"]  
        columns = [-1, -2, -3, -4, -5, -6 ]
        self.Open_Orders_Record = [columns]
        self.closed_orders_record = [columns]  #Já existe um outro registo do histórico, isto deve perder a função

        logs.log(info_msg="[Created Object] Order_record  actor:"+str(self.actor)) 
        
        
#---------------------------------------------------------------------     
    def filter_by_product(self,complete_history,product):
            filter_arr = []
            
            for element in complete_history:
                if element[1] == product:
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
        print("\n get inventory: \n",self.Open_Orders_Record)
        return self.record


# \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ 
    def add_to_open_orders(self,  product, qty, client):
        logs.log(debug_msg="[FUNCION] with parameters: time:" + str(self.actor.simulation.time ) + " product: "+ str(product) + " Qty " + str(qty) + " Client: "+ str(client))
        actor_id = self.actor
        
        self.last_order_id = self.last_order_id + 1
        #initial status = 0
        to_add = [self.actor.simulation.time  ,product, qty,  client, self.last_order_id, 0]

        self.Open_Orders_Record.append(to_add) 

        logs.log(debug_msg="[ORDERED ADDED]  Products ordered from"+str(self.actor)+" Parameters "+str(to_add))
        
        self.add_to_orders_log( product, qty, client, self.last_order_id ,  status = 0)
    
    def add_to_orders_log(self, product, qty, client, order_id, status): 
        with open( str( sim_cfg.orders_record_path ) + "orders_record_" + str( self.actor.id ) + ".csv", 'a') as file:
            file.write( str(self.actor.simulation.time)  +","+ str(product) + "," + str(qty) + "," + str(client)+ "," + str(order_id) + ","+ str(status)+ "\n")


    # #check the order id and changes the status
    # def set_order_status(self, order_id, status):
    #     for record in self.Open_Orders_Record:
    #         if record[-2] == order_id:
    #             record[-1] = status
    #     self.remove_from_open_orders(order_id)

    def remove_from_open_orders(self,  order_id):
        time = self.actor.simulation.time 

        for record in self.Open_Orders_Record:
            if record[-2] == order_id and record[-1] == 1:
                record[1] = time
                self.Open_Orders_Record.remove(record) 
                self.closed_orders_record.append(record)
        logs.log(debug_msg=" order "+str(order_id)+" removed from actor "+str(self.actor))


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







