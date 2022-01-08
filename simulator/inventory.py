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
            #del product["initial_stock"]                               #isto vai ser informação denecessária mas vamos manter para já
            self.main_inventory[product['id']]=product
            
            self.actor.simulation.mongo_db.update_inventory_db(actor_id=self.actor.id, product=product['id'], quantity=product['in_stock'])
            
            try: self.actor.simulation.cookbook[product['id']] = product['composition']
            except:   logs.log(debug_msg="| CREATED OBJECT   | inventory     producto sem composição:"+str(product))

        if self.actor.id == 0:
            null_product={'name': 'Product_Null', 'id': 0000, 'initial_stock': 0, 'safety_stock': 0, 'reorder_history_size': 0, 'composition': {'0000': 0}, 'in_stock': 0}
            self.main_inventory[0000]=null_product
            self.actor.simulation.mongo_db.update_inventory_db(actor_id=0, product=0, quantity=0)
        
        self.present_capacity = self.refresh_inventory_capacity()
        # self.update_inicial_inventory()

        logs.log(info_msg="| CREATED OBJECT   | inventory     actor:"+str(actor))
#-----------------------------------------------------------------
    # def  update_inicial_inventory(self):
    #     for product in self.products:
    #         #self.actor.simulation.update_global_inventory( self.actor.id ,product['id'], product['in_stock'] )
    #         self.actor.simulation.mongo_db.update_inventory_db(actor_id=self.actor.id, product=product['id'], quantity=product['in_stock'])
    #     self.actor.simulation.mongo_db.update_inventory_db(actor_id=0, product=0, quantity=0)


    def add_to_inventory(self, product, quantity):
        logs.log(debug_msg="| FUNCTION         | inventory.add_to_inventory of actor {} product {} qty {}".format(self.actor.id, product, quantity))
        new_product=False

        present_stock = self.get_product_inventory(product)
        if present_stock is False:
            present_stock = 0
            new_product = True

        updated_stock = present_stock + quantity
        #quantidade inválida
        if quantity < 0:
            raise Exception("trying to add negative quantity")

        #excede a capacidade de armazenamento
        elif (self.present_capacity  + quantity) > self.max_capacity:
            logs.log(debug_msg="| FUNCTION         | inventory     | inventory.add_to_inventory    Inventory full")
            return False

        #if will not pass the max inventory
        else:
            self.set_product_inventory(product_id=product, new_quantity = updated_stock)

            self.actor.simulation.mongo_db.update_inventory_db(self.actor.id, product, updated_stock)

            #self.actor.simulation.update_global_inventory( self.actor.id ,product, quantity )                        #update the global inventory used in the dashboard
            logs.log(debug_msg="| FUNCTION         | inventory     | inventory.add_to_inventory  now product added Sucess!! ")
            return True
        
  
        # else:
        #     print("actor {}, product {}, inventory {} ".format(type(self.actor), type(product) ,self.main_inventory[product]))
        #     logs.log(debug_msg="| FUNCTION         | inventory     | inventory.add_to_inventory  ERROR product does not exist !! get inventory actor: {} product: {} | inventory:{} main inventory:{}".format( self.actor, product ,self.main_inventory[product['in_stock']] ,   self.main_inventory ))
        #     return False



    def remove_from_inventory(self,  product, quantity):
        logs.log(debug_msg  = "| FUNCTION         | inventory     | trying to remove_from_inventory actor:{} product:{} qty:{}".format(self.actor.id, product, quantity))
        
        
        present_stock = self.get_product_inventory(product)
        
        #se não existir o producto, o stock é zero
        if present_stock is False:    #present_stock = 0
            return False
            

        updated_stock= present_stock-quantity

        #se não tiver quantidade em stock para enviar devolve falso
        if updated_stock < 0:
            logs.log(debug_msg  = "| FUNCTION         | inventory     | remove_from_inventory not enough stock of product {} for odered qty of {} in actor {}. actual stock:{}".format(product, quantity, self.actor.id,product_stock)) 
            return False
        
        #se o stock não é zero, e a quantidade é maior que o stock, envia
        else:
            self.set_product_inventory(product_id= product, new_quantity=updated_stock)
            return True
            #atualiza do stock global
            
            #print("temp remove {} from ",self.get_product_inventory(product))
            #self.actor.simulation.update_global_inventory(actor_id= actor_id, product_id= product, quantity = new_quantity )
            logs.log(debug_msg  = "| FUNCTION         | inventory     | remove_from_inventory SUCESS!!!! product {} for odered qty of {}".format(product, quantity))



#############################################
    def get_product_inventory(self, product_id):
        logs.log(debug_msg="| FUNCTION         | inventory     | get product_inv "+str( self.actor.id)+' product '+str(product_id)+" stock==="+str(self.main_inventory))
    
        # try:
            #print("tempget product",self.main_inventory[int(product_id)])
            #print("tempget product",self.main_inventory[product_id]["in_stock"])
        #print("has",type(self.main_inventory), product_id in self.main_inventory)
        product_id=int(product_id)
        # print("A get porduct",product_id, "actor, ", self.actor.id)
        # print("B",self.main_inventory)
        # print("C",self.main_inventory[product_id])
        # print("D",self.main_inventory[product_id]["in_stock"])
        if product_id in self.main_inventory:
            if "in_stock" in self.main_inventory[product_id]:
                return self.main_inventory[product_id]["in_stock"]
            if "in_stock" not in self.main_inventory[product_id]:
                print("deu merda")
        else:
            return False
        
    
        # except:
        #     logs.log(debug_msg="| FUNCTION         | inventory     | get_product_inventory EXCEPT RAISED, PRODUCT STOCK UNKNOW, RETURNED ZERO actor "+str( self.actor.id)+' product '+str(product_id)+""+self.main_inventory[product_id]["in_stock"])
        #     return False


    def get_product_safety_stock(self, product_id):
        logs.log(debug_msg="| FUNCTION         | inventory     | get product safety stock "+str( self.actor.id)+' product '+str(product_id))
        # import inspect
        # print(inspect.stack())

        product_id=int(product_id)
   
   
        if product_id in self.main_inventory:
            if "in_stock" in self.main_inventory[product_id]:
                return self.main_inventory[product_id]["safety_stock"]
            if "in_stock" not in self.main_inventory[product_id]:
                print("deu merda")
        else:
            return False
        

    def set_product_inventory(self, product_id, new_quantity):
        logs.log(debug_msg="| FUNCTION         | inventory     |set_product_inventory "+str( self.actor.id)+' product '+str(product_id) )
        product_id=int(product_id)
        if self.get_product_inventory( product_id) is False:
                                   
            self.main_inventory[product_id] = {'id': product_id, 'in_stock': new_quantity}
        
        else:
            self.main_inventory[product_id]["in_stock"] = new_quantity
        self.actor.simulation.mongo_db.update_inventory_db(actor_id = self.actor.id, product=product_id, quantity=new_quantity )
        logs.log(debug_msg="| FUNCTION         | inventory     | set_product_inventory inventory of {} updated to {} ".format(product_id, new_quantity ))
        return True





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
        
