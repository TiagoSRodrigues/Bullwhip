from . import transactions, logging_management as logs
import pandas as pd,  simulation_configuration  as sim_cfg, csv, numpy as np, json

logs.log(debug_msg="Started Inventory.py")

"""
PARA JÁ O INVENTÁRIO TERÁ APENAS UM PRODUTO, FICA A IDEIA DE DEPOIS ADICIONAR OUTROS, 
a classe inventário passará a ter uma classe filha de produtos
"""


class ClassInventory:
    def __init__(self,
                actor,
                max_capacity, products):

        self.actor           = actor
        self.max_capacity    = max_capacity
        self.products        = products
        
        self.main_inventory=dict()
    
        for product in products:

            #change the key initial to in_stock
            product["in_stock"] = product["initial_stock"]
            del product["initial_stock"]
            self.main_inventory[product['id']]=product
            try: self.actor.simulation.cookbook[product['id']] = product['composition']
            except:   logs.log(debug_msg="| CREATED OBJECT   | inventory     producto sem composição:"+str(product))


        self.present_capacity = self.refresh_inventory_capacity()
        self.update_inicial_inventory()

        logs.log(info_msg="| CREATED OBJECT   | inventory     actor:"+str(actor))
#-----------------------------------------------------------------
    def  update_inicial_inventory(self):
        for product in self.products:
            self.actor.simulation.update_global_inventory( self.actor.id ,product['id'],product['in_stock'] )


    def add_to_inventory(self, product, quantity):
        logs.log(debug_msg="| FUNCTION         | inventory.add_to_inventory"+str( self)+str(product)+str(quantity))

        #check if product inventory exists, if not creats it
        present_capacity=self.check_inventory_composition()
        if quantity < 0:
            return False 
        #check if exists and if will not pass the max if created
        elif self.products_inventory.get_product_inventory(product) == None and quantity + self.check_inventory_composition() <= self.max_capacity :
            self.products_inventory[product] = quantity
            self.actor.simulation.update_global_inventory( self.actor.id ,product,quantity )
            return True
        
        elif present_capacity  + quantity > self.max_capacity:
            return False
        
        else:
            self.products_inventory[product] = self.products_inventory.get_product_inventory(product)  + quantity
            self.actor.simulation.update_global_inventory( self.actor.id ,product,quantity )

            return True 

    def remove_from_inventory(self, product, quantity):
        logs.log(debug_msg  = "| FUNCTION         | inventory     | remov_inventory" + str(product) + str(quantity))
        product_stock       = int(self.get_product_inventory(product))
        print("XXXXXXXXXX",product,quantity)
        
        if self.get_product_inventory(product) == None:
            product_stock = 0

        elif product_stock - quantity <=0 :
            print("ERRO A REMOVER PRODUCTO - ELIF DO INVENTORY LINE 64 ")
            return False
        
        else:
            # print("else:" ,product_stock - quantity)
            self.main_inventory[product]["in_stock"] = (product_stock - quantity)
            self.actor.simulation.update_global_inventory(actor_id= self.actor.id, product_id=product, quantity= quantity*-1 )


            return True 
        
    def check_inventory_composition(self):
        header = "Inventory of: "+ str( self.actor.id )+  "\nPresent capacity: " + str(self.present_capacity) +" of  a max  of  " +str( self.max_capacity )
        table , cols =[], [ " id "," Name "," in_stock "," safety_stock "]
       
        for product in self.products:
            table.append( [ product['id'] , product['name'] ,product['in_stock'] ,product['safety_stock'] ] )
        
        x=pd.DataFrame(data=table, columns=cols)
        # print("\n",header,"\n",  x.to_string(index=False), "\n")




#############################################
    def get_product_inventory(self, product_id):
        logs.log(debug_msg="| FUNCTION         | inventory     | product_inv "+str( self.actor.id)+' product '+str(product_id))

        try: 
            return self.main_inventory[product_id]["in_stock"]
        except:
            logs.log(debug_msg="| FUNCTION         | inventory     | get_product_inventory EXCEPT RAISED, PRODUCT STOCK UNKNOW, RETURNED ZERO"+str( self.actor.id)+' product '+str(product_id)+"")
            return 0

    def get_product_safety_inventory(self, product_id):
        logs.log(debug_msg="| FUNCTION         | inventory     | get_product_safety_inventory " + str( self.actor.id)+' product '+str(product_id))

        try:     
            return self.main_inventory[product_id]["safety_stock"]
        except:
            print(self.main_inventory)
            logs.log(warning_msg="Error on get_product_safety_inventory, check product id "+str(product_id))
            print("Error on get_product_safety_inventory")


    def get_product_reorder_history_size(self, product_id):
        logs.log(debug_msg="| FUNCTION         | inventory     | get_product_reorder_history_size " + str( self.actor.id)+' product '+str(product_id))

        try:
            print("YYYYYYYYYYY",self.main_inventory[product_id]["reorder_history_size"])     
            return self.main_inventory[product_id]["reorder_history_size"]
        except:
            logs.log(warning_msg="Error on get_product_reorder_history_size, check product id "+str(product_id))

    def refresh_inventory_capacity(self):
        logs.log(debug_msg="| FUNCTION         | inventory     | get_product_inventory "+str( self.actor.id))

        self.present_capacity=0
        for product in self.main_inventory:
            self.present_capacity = self.present_capacity + self.main_inventory[product]['in_stock']


        if self.present_capacity > self.max_capacity:
            logs.log(warning_msg="OVERCAPACITY in actor: "+str(self.actor.id)+"  | Stock is " + str(self.present_capacity) + " of a max of "+ str(self.max_capacity)) 

        return self.present_capacity

######################################################################
    def show_present_composition(self):
        print("\nInventory present size=" ,self.check_inventory_composition())
        print("\nInventory present size=" ,self.main_inventory)

        # for key ,value  in self.main_inventory.items():
        #     print("xx",key, value) #self.products_inventory[key]) 
        
