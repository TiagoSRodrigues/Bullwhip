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
        
        self.main_inventory={}
    
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
            self.actor.simulation.update_global_inventory( self.actor.id ,product['id'], product['in_stock'] )


    def add_to_inventory(self, product, quantity):
        logs.log(debug_msg="| FUNCTION         | inventory.add_to_inventory of actor {} product {} qty {}".format(self.actor.id, product, quantity))

        #check if product inventory exists, if not creats it

        if quantity < 0:
            return False 

        elif self.present_capacity  + quantity > self.max_capacity:
            return False

        #if productc does not exists in stock and if will not pass the max inventory, is  created
        elif  self.get_product_inventory(product) == False :
            print("add_to_inventory error", self.get_product_inventory(product))

            self.main_inventory[product] = { 'id': product, 'in_stock': quantity}

            self.actor.simulation.update_global_inventory( self.actor.id ,product,quantity )                        #update the global inventory used in the dashboard
            logs.log(debug_msg="| FUNCTION         | inventory     | inventory.add_to_inventory  now product added Sucess!! ")
            return True
        
        
        else:
            try:
                if self.set_product_inventory( product, self.get_product_inventory(product) +quantity) == True:
                    self.actor.simulation.update_global_inventory( self.actor.id ,product,quantity )
                    logs.log(debug_msg="| FUNCTION         | inventory     | inventory.add_to_inventory  Sucess!! ")
                    return True


            except:
                logs.log(debug_msg="| FUNCTION         | inventory     | inventory.add_to_inventory  ERROR product does not exist !! get inventory actor: {} product: {} | inventory:{} main inventory:{}".format( self.actor.id, product ,self.main_inventory[product['in_stock']] ,   self.main_inventory ))
                return False



    def remove_from_inventory(self, product, quantity):
        logs.log(debug_msg  = "| FUNCTION         | inventory     | trying to remove_from_inventory actor:{} product:{} qty:{}".format(self.actor, product, quantity))
        product_stock       = int(self.get_product_inventory(product))
        
        #se não existir o producto, o stock é zero
        if self.get_product_inventory(product) is None:
            product_stock = 0

        #se não tiver quantidade em stock para enviar devolve falso
        elif (product_stock - quantity) < 0 :
            logs.log(debug_msg  = "| FUNCTION         | inventory     | remove_from_inventory not enough stock of product {} for odered qty of {} in actor {}. actual stock:{}".format(product, quantity, self.actor.id,product_stock)) 
            return False
        
        #se o stock não é zero, e a quantidade é maior que o stock, envia
        else:
            #remove do stock do ator
            self.main_inventory[product]["in_stock"] = (product_stock - quantity)
            #atualiza do stock global
            self.actor.simulation.update_global_inventory(actor_id= self.actor.id, product_id=product, quantity = (product_stock - quantity) )
            logs.log(debug_msg  = "| FUNCTION         | inventory     | remove_from_inventory SUCESS!!!! product {} for odered qty of {}".format(product, quantity)) 
            return True
        
    # def check_inventory_composition(self):
    #     header = "Inventory of: "+ str( self.actor.id )+  "\nPresent capacity: " + str(self.present_capacity) +" of  a max  of  " +str( self.max_capacity )
    #     table , cols =[], [ " id "," Name "," in_stock "," safety_stock "]
       
    #     for product in self.products:
    #         table.append( [ product['id'] , product['name'] ,product['in_stock'] ,product['safety_stock'] ] )
        
    #     x=pd.DataFrame(data=table, columns=cols)
    #     # print("\n",header,"\n",  x.to_string(index=False), "\n")
        




#############################################
    def get_product_inventory(self, product_id):
        logs.log(debug_msg="| FUNCTION         | inventory     | get product_inv "+str( self.actor.id)+' product '+str(product_id)+" stock==="+str(self.main_inventory))
        
       
        try: 
            return self.main_inventory[int(product_id)]["in_stock"]
        except:
            logs.log(debug_msg="| FUNCTION         | inventory     | get_product_inventory EXCEPT RAISED, PRODUCT STOCK UNKNOW, RETURNED ZERO"+str( self.actor.id)+' product '+str(product_id)+"")
            return False

    def set_product_inventory(self, product_id, qty):
        logs.log(debug_msg="| FUNCTION         | inventory     |set_product_inventory "+str( self.actor.id)+' product '+str(product_id) )
        
        try: 
            self.main_inventory[int(product_id)]["in_stock"] = qty
            return True
        except:
            logs.log(debug_msg="| FUNCTION         | inventory     | set_product_inventory ERROR ")
            return False





    def get_product_safety_inventory(self, product_id):
        logs.log(debug_msg="| FUNCTION         | inventory     | get_product_safety_inventory " + str( self.actor.id)+' product '+str(product_id))

        try:     
            return self.main_inventory[product_id]["safety_stock"]
        except:
            print("get_product_safety_inventory error:", self.main_inventory)
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

        present_capacity=0

        for product in self.main_inventory:
            present_capacity = present_capacity + self.main_inventory[product]['in_stock']

        if present_capacity > self.max_capacity:
            logs.log(warning_msg="OVERCAPACITY in actor: "+str(self.actor.id)+"  | Stock is " + str(present_capacity) + " of a max of "+ str(self.max_capacity)) 

        if present_capacity < 0: 
                raise Exception( logs.log(warning_msg="Inventário negativo!!! no ator: {}".format(self.actor.id)))

        self.present_capacity = present_capacity
        return present_capacity

######################################################################
    def show_present_composition(self):
        print("\nInventory present size=" ,self.main_inventory)

        # for key ,value  in self.main_inventory.items():
        #     print("xx",key, value) #self.products_inventory[key]) 
        
