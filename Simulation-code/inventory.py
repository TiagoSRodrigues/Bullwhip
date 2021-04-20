import transactions
import logging_management as logs
logs.log(debug_msg="Started Inventory.py")

"""
PARA JÁ O INVENTÁRIO TERÁ APENAS UM PRODUTO, FICA A IDEIA DE DEPOIS ADICIONAR OUTROS, 
a classe inventário passará a ter uma classe filha de produtos
""""


class ClassInventory:
    def __init__(self, actor,max_capacity:int):
        self.actor = actor
        self.max_inventory = max_inventory

        logs.log(info_msg="[Created Object] inventory     actor:"+str(actor))



    def get_inventory(self):
        print("get_inventory",self.actual_stock)
        return self.actual_stock

    def check_inventory_full(self):
        return self.actual_stock==self.max_inventory

    def check_inventory_empty(self):
        return self.actual_stock==0


    #retorna true se conseguiu, retorna false se não conseguiu
    def add_to_inventory(self,qty:int,product=None):
        if qty<0:
            return False 
        elif self.check_inventory_full():
            return False
        elif self.actual_stock+qty > self.max_inventory:
            return False
        else:
            self.actual_stock = self.actual_stock+qty
            return  True

    def remove_from_inventory(self,qty:int,product=None):
        if qty<0:
            return False
        elif self.check_inventory_empty():
            return False
        elif self.actual_stock - qty < 0:
            return False            
        else:
            self.actual_stock = self.actual_stock-qty
            return True 

    def manage_stock(self):
        actor=self.actor
        historical_order = actor.get_ordered_products(self,time_interval=None,product=None)
        if self.actual_stock <= self.safety_stock:
            transactions.process_order(historical_order)
    

class ClassProductInventory(ClassInventory):
    def __init__(self,
                actor,
                initial_stock,
                safety_stock,
                max_inventory,
                product=None):
        super().__init__(actor,
                         initial_stock,
                         safety_stock,
                         max_inventory,
                         product=product)







#Esta função analisa o histórico definido e se o stock for inferior ao minimo encomenda
# # a quantidade igual à expedida, até ao máximo definido (se existir). 
# # TLDR Verifica se deve encomendar mais
# def manage_stock(actor, min_stock, history_size, max_stock=None,):
#     stock = actor.get_stock()
#     pass





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
