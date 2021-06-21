import transactions
import logging_management as logs
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
            

        present_capacity = self.refresh_inventory_capacity()

        logs.log(info_msg="[Created Object] inventory     actor:"+str(actor))
#-----------------------------------------------------------------
    def add_to_inventory(self, product, quantity):
        #check if product inventory exists, if not creats it
        present_capacity=self.check_inventory_composition()
        if quantity < 0:
            return False 
        #check if exists and if will not pass the max if created
        elif self.products_inventory.get(product) == None and quantity + self.check_inventory_composition() <= self.max_capacity :
            self.products_inventory[product] = quantity
            return True
        
        elif present_capacity  + quantity > self.max_capacity:
            return False
        
        else:
            self.products_inventory[product] = self.products_inventory.get(product)  + quantity
            return True 

    def remove_from_inventory(self, product, quantity):
        logs.log(debug_msg  = "[method] remove_from_inventory" + str(product) + str(quantity))
        present_capacity    = self.check_inventory_composition()
        product_stock       = self.products_inventory.get(product)
        
        if self.products_inventory.get(product) == None:
            product_stock=0
        
        if quantity < 0:
            return False
        
        elif product_stock - quantity <=0 :
            return False
        
        else:
            self.products_inventory[product] = self.products_inventory.get(product) - quantity
            return True 
        
    def check_inventory_composition(self):
        header = "Inventory of: "+ str( self.actor )+  "\nPresent capacity: " + str(self.present_capacity) +" of  a max  of  " +str( self.max_capacity )
        table , cols =[], [ " id "," Name "," in_stock "," safety_stock "]
       
        for product in self.products:
            table.append( [ product['id'] , product['Name'] ,product['in_stock'] ,product['safety_stock'] ] )
        
        x=pd.DataFrame(data=table, columns=cols)
        print("\n",header,"\n",  x.to_string(index=False), "\n")




#############################################
    def get_product_inventory(self, product_id):
        try:
            return self.main_inventory[product_id]["in_stock"]
        except:
            logs.log(warning_msg="Error on get_product_inventory, check product id")
            print("Error on product inventory")









    def refresh_inventory_capacity(self):
        self.present_capacity=0
        for product in self.main_inventory:
            self.present_capacity = self.present_capacity + self.main_inventory[product]['in_stock']
        if self.present_capacity > self.max_capacity:
            logs.log(warning_msg="OVERCAPACITY in actor: "+str(self.actor)+"  | Stock is " + str(self.present_capacity) + " of a max of "+ str(self.max_capacity)) 


######################################################################
    def show_present_composition(self):
        # print("Inventory present size=" ,self.check_inventory_composition(),"\n")
        for key ,value  in self.products_inventory.items():
            print(key, value) #self.products_inventory[key]) 
        

    def manage_stock(self):
        actor=self.actor
        historical_order = actor.get_ordered_products(self,time_interval=None,product=None)
        if self.actual_stock <= self.safety_stock:
            transactions.process_order(historical_order)
    



# a=ClassInventory("Simone",max_capacity=400)

# a.show_present_composition()                                    
# a.add_to_inventory(product      ="Bananas",quantity=100)    #100
# a.remove_from_inventory(product ="Bananas",quantity=10)     #110
# a.add_to_inventory(     product ="mor",    quantity=10)     #120
# a.add_to_inventory(     product ="franb",  quantity=110)    #230 
# a.add_to_inventory(     product ="franb",  quantity=70)     #300
# a.add_to_inventory(     product ="franb",  quantity=90)     #390
# a.add_to_inventory(     product ="Ananas", quantity=20)     #390
# a.add_to_inventory(     product ="mel",    quantity=10)     #400
# a.add_to_inventory(     product ="mela",   quantity=100)    #400


# print("product inventory", a.check_product_inventory( "Bananas"))
# a.remove_from_inventory(product="Ananas",quantity=1000)#product="mel",quantity=100)


# a.show_present_composition()



#Esta função analisa o histórico definido e se o stock for inferior ao minimo encomenda
# # a quantidade igual à expedida, até ao máximo definido (se existir). 
# # TLDR Verifica se deve encomendar mais
# def manage_stock(actor, min_stock, history_size, max_stock=None,):
#     stock = actor.get_stock()
#     pass


# {
#     "productA":"qty",
#     "productB":"qty"

# }




# a=inventory("tiago","a",95,5,100)
# a.get_inventory()
# print("\n",a.add_to_inventory(qty=3))
# a.get_inventory()
# print("\n",a.add_to_inventory(qty=-2))
# a.get_inventory()
# print("\n",a.add_to_inventory(qty=1))
# a.get_inventory()
# print("\n",a.add_to_inventory(qty=2))
# a.get_inventory()
# print("\n",a.add_to_inventory(qty=3))
# a.get_inventory()
# print("\n",a.add_to_inventory(qty=1))
# a.get_inventory()

# print("\n",a.remove_from_inventory(qty=101))
# a.get_inventory()
