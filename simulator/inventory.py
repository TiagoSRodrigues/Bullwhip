from . import transactions, logging_management as logs
import pandas as pd
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
            

        self.present_capacity = self.refresh_inventory_capacity()

        logs.log(info_msg="[Created Object] inventory     actor:"+str(actor))
#-----------------------------------------------------------------
    def add_to_inventory(self, product, quantity):
        logs.log(debug_msg="[Function] inventory.add_to_inventory"+str( self)+str(product)+str(quantity))

        #check if product inventory exists, if not creats it
        present_capacity=self.check_inventory_composition()
        if quantity < 0:
            return False 
        #check if exists and if will not pass the max if created
        elif self.products_inventory.get_product_inventory(product) == None and quantity + self.check_inventory_composition() <= self.max_capacity :
            self.products_inventory[product] = quantity
            return True
        
        elif present_capacity  + quantity > self.max_capacity:
            return False
        
        else:
            self.products_inventory[product] = self.products_inventory.get_product_inventory(product)  + quantity
            return True 

    def remove_from_inventory(self, product, quantity):
        logs.log(debug_msg  = "[method] remove_from_inventory" + str(product) + str(quantity))
        product_stock       = self.get_product_inventory(product)
        
        if self.get_product_inventory(product) == None:
            product_stock = 0

        elif product_stock - quantity <=0 :
            print("ERRO A REMOVER PRODUCTO - ELIF DO INVENTORY LINE 64 ")
            return False
        
        else:
            # print("else:" ,product_stock - quantity)
            self.main_inventory[product]["in_stock"] = (product_stock - quantity)
            return True 
        
    def check_inventory_composition(self):
        header = "Inventory of: "+ str( self.actor )+  "\nPresent capacity: " + str(self.present_capacity) +" of  a max  of  " +str( self.max_capacity )
        table , cols =[], [ " id "," Name "," in_stock "," safety_stock "]
       
        for product in self.products:
            table.append( [ product['id'] , product['Name'] ,product['in_stock'] ,product['safety_stock'] ] )
        
        x=pd.DataFrame(data=table, columns=cols)
        # print("\n",header,"\n",  x.to_string(index=False), "\n")




#############################################
    def get_product_inventory(self, product_id):
        logs.log(debug_msg="[Function] inventory.get_product_inventory"+str( self)+str(product_id))
        try:
            return self.main_inventory[product_id]["in_stock"]
        except:
            logs.log(warning_msg="Error on get_product_inventory, check product id")
            print("Error on get_product_inventory")

    def get_product_safety_inventory(self, product_id):
        logs.log(debug_msg="[Function] inventory.get_product_inventory"+str( self)+str(product_id))
        try:     
            return self.main_inventory[product_id]["safety_stock"]
        except:
            print(self.main_inventory)

            logs.log(warning_msg="Error on get_product_safety_inventory, check product id")
            print("Error on get_product_safety_inventory")

    def refresh_inventory_capacity(self):
        logs.log(debug_msg="[Function] inventory.get_product_inventory"+str( self))

        self.present_capacity=0
        for product in self.main_inventory:
            self.present_capacity = self.present_capacity + self.main_inventory[product]['in_stock']
        
        if self.present_capacity > self.max_capacity:
            logs.log(warning_msg="OVERCAPACITY in actor: "+str(self.actor)+"  | Stock is " + str(self.present_capacity) + " of a max of "+ str(self.max_capacity)) 

        return self.present_capacity

######################################################################
    def show_present_composition(self):
        # print("Inventory present size=" ,self.check_inventory_composition(),"\n")
        for key ,value  in self.products_inventory.items():
            print(key, value) #self.products_inventory[key]) 
        


