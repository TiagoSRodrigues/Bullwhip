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

            self.main_inventory[int(product['id'])]=product

            self.actor.simulation.mongo_db.update_inventory_db(actor_id=self.actor.id, product=product['id'], quantity=product['in_stock'])

            try: self.actor.simulation.cookbook[product['id']] = product['composition']
            except:
                logs.new_log(state=self.actor.actor_state, actor=self.actor.id, file="inventory", function="constructor", day=self.actor.simulation.time,  debug_msg=  f"product {product['id']} without composition" )


        if self.actor.id == 0:
            null_product={'name': 'Product_Null', 'id': 0000, 'initial_stock': 0, 'safety_stock': 0,  'composition': {'0000': 0}, 'in_stock': 0}
            self.main_inventory[0000]=null_product
            self.actor.simulation.mongo_db.update_inventory_db(actor_id=0, product=0, quantity=0)

        self.present_capacity = self.refresh_inventory_capacity()
        # self.update_inicial_inventory()

        logs.new_log(state=self.actor.actor_state, actor=self.actor.id, file="inventory", function="constructor", day=self.actor.simulation.time,  debug_msg=  f"Inventory created" )
#-----------------------------------------------------------------
    # def  update_inicial_inventory(self):
    #     for product in self.products:
    #         #self.actor.simulation.update_global_inventory(self.actor.id ,product['id'], product['in_stock'] )
    #         self.actor.simulation.mongo_db.update_inventory_db(actor_id=self.actor.id, product=product['id'], quantity=product['in_stock'])
    #     self.actor.simulation.mongo_db.update_inventory_db(actor_id=0, product=0, quantity=0)







    #                                                                                    tttt
    #                                                                                ttt:::t
    #                                                                                t:::::t
    #                                                                                t:::::t
    #                                    ggggggggg   ggggg    eeeeeeeeeeee    ttttttt:::::tttttttttttttt
    #                                    g:::::::::ggg::::g  ee::::::::::::ee  t:::::::::::::::::tt:::::
    #                                    g:::::::::::::::::g e::::::eeeee:::::eet:::::::::::::::::tt::::
    #                                    g::::::ggggg::::::gge::::::e     e:::::etttttt:::::::tttttttttt
    #                                    g:::::g     g:::::g e:::::::eeeee::::::e      t:::::t
    #                                    g:::::g     g:::::g e:::::::::::::::::e       t:::::t
    #                                    g:::::g     g:::::g e::::::eeeeeeeeeee        t:::::t
    #                                    g::::::g    g:::::g e:::::::e                 t:::::t    tttttt
    #                                    g:::::::ggggg:::::g e::::::::e                t::::::tttt:::::t
    #                                    g::::::::::::::::g  e::::::::eeeeeeee        tt::::::::::::::t
    #                                    gg::::::::::::::g   ee:::::::::::::e          tt:::::::::::tt
    #                                        gggggggg::::::g     eeeeeeeeeeeeee            ttttttttttt
    #                                                g:::::g
    #                                    gggggg      g:::::g
    #                                    g:::::gg   gg:::::g
    #                                    g::::::ggg:::::::g
    #                                    gg:::::::::::::g



    def update_product_waiting_stock(self, product_id, quantity):
        self.main_inventory[product_id]["waiting_stock"] = quantity

    def get_actor_inventory(self):
        return self.main_inventory

    def get_product_safety_inventory(self, product_id):
        logs.new_log(state=self.actor.actor_state, actor=self.actor.id, file="inventory", function="get_product_safety_inventory", day=self.actor.simulation.time,  debug_msg= f" get_product_safety_inventory {str(self.actor.id)} product {str(product_id)}" )

        try:
            return self.main_inventory[product_id]["safety_stock"]
        except:
            Exception("get_product_safety_inventory error:", self.main_inventory)

    def get_product_stock(self, product_id:int):
        product_id = int(product_id)


        product_id=int(product_id)
        if product_id in self.main_inventory:
            if "in_stock" in self.main_inventory[product_id]:
                return self.main_inventory[product_id]["in_stock"]

            if "in_stock" not in self.main_inventory[product_id]:
                raise Exception("product not in inventory")
        else:
            logs.new_log(state=self.actor.actor_state, actor=self.actor.id, file="inventory", function="get_product_stock", day=self.actor.simulation.time,  debug_msg=  f"product {product_id} not in inventory" )
            return False


    def get_product_safety_stock(self, product_id:int):
        product_id = int(product_id)
        logs.new_log(state=self.actor.actor_state, actor=self.actor.id, file="inventory", function="get_product_safety_stock", day=self.actor.simulation.time,  debug_msg=  f"get product safety stock {str(self.actor.id)} product {str(product_id)}" )

        product_id=int(product_id)


        if product_id in self.main_inventory:
            if "in_stock" in self.main_inventory[product_id]:
                return self.main_inventory[product_id]["safety_stock"]
            if "in_stock" not in self.main_inventory[product_id]:
                print("deu merda")
        else:
            return False

    #
    #
    #                                                         tttt
    #                                                          ttt:::t
    #                                                          t:::::t
    #                                                          t:::::t
    #                   ssssssssss       eeeeeeeeeeee    ttttttt:::::ttttttt
    #                 ss::::::::::s    ee::::::::::::ee  t:::::::::::::::::t
    #               ss:::::::::::::s  e::::::eeeee:::::eet:::::::::::::::::t
    #               s::::::ssss:::::se::::::e     e:::::etttttt:::::::tttttt
    #                s:::::s  ssssss e:::::::eeeee::::::e      t:::::t
    #                  s::::::s      e:::::::::::::::::e       t:::::t
    #                     s::::::s   e::::::eeeeeeeeeee        t:::::t
    #               ssssss   s:::::s e:::::::e                 t:::::t    tttttt
    #               s:::::ssss::::::se::::::::e                t::::::tttt:::::t
    #               s::::::::::::::s  e::::::::eeeeeeee        tt::::::::::::::t
    #                s:::::::::::ss    ee:::::::::::::e          tt:::::::::::tt
    #                 sssssssssss        eeeeeeeeeeeeee            ttttttttttt
    #
    #
    def set_product_inventory(self, product_id:int, new_quantity:int):
        product_id, new_quantity = int(product_id), int(new_quantity)
        logs.new_log(state=self.actor.actor_state, actor=self.actor.id, file="inventory", function="set_product_inventory", day=self.actor.simulation.time,  debug_msg= f"setting {new_quantity} to prd  {product_id} | present inventory {self.main_inventory}" )
        # print("keys")
        # for key in self.main_inventory:
            # print(key, type(key))

        # se não existir no inventário, cria
        # print("actor", self.actor.id , self.main_inventory)

        present_stock = self.get_product_stock(product_id)
        if present_stock is False:
            #produto novo, é adicionado ao inventário
            self.main_inventory[product_id] = {'id': product_id, 'in_stock': new_quantity}
            logs.new_log(state=self.actor.actor_state, actor=self.actor.id, file="inventory", function="set_product_inventory", day=self.actor.simulation.time,debug_msg= f"producto nao existia, foi adicionado" )
            return True

        #se existe no inventário
        self.main_inventory[product_id]["in_stock"] = new_quantity
        self.actor.simulation.mongo_db.update_inventory_db(actor_id = self.actor.id, product=product_id, quantity=new_quantity )

        logs.new_log(state=self.actor.actor_state, actor=self.actor.id, file="inventory", function="set_product_inventory", day=self.actor.simulation.time,debug_msg= f"inventory of {product_id} updated to {new_quantity}" )

        return True


    def set_product_safety_inventory(self, product_id, quantity):
        logs.new_log(state=self.actor.actor_state, actor=self.actor.id, file="inventory", function="set_product_safety_inventory", day=self.actor.simulation.time,debug_msg=  "actor{} product {} qty {}".format(self.actor.id, product_id, quantity ) )

        try:
            self.main_inventory[product_id]["safety_stock"] = quantity
            return True
        except:
            print("get_product_safety_inventory error:", self.main_inventory)
            logs.log(warning_msg="Error on get_product_safety_inventory, check product id "+str(product_id))
            print("Error on get_product_safety_inventory")





        #                                                                         tttt
        #                                                                     ttt:::t
        #                                                                     t:::::t
        #                                                                     t:::::t
        #                             aaaaaaaaaaaaa      ccccccccccccccccttttttt:::::ttttttt
        #                             a::::::::::::a   cc:::::::::::::::ct:::::::::::::::::t
        #                             aaaaaaaaa:::::a c:::::::::::::::::ct:::::::::::::::::t
        #                                     a::::ac:::::::cccccc:::::ctttttt:::::::tttttt
        #                                 aaaaaaa:::::ac::::::c     ccccccc      t:::::t
        #                             aa::::::::::::ac:::::c                   t:::::t
        #                             a::::aaaa::::::ac:::::c                   t:::::t
        #                             a::::a    a:::::ac::::::c     ccccccc      t:::::t    tttttt
        #                             a::::a    a:::::ac:::::::cccccc:::::c      t::::::tttt:::::t
        #                             a:::::aaaa::::::a c:::::::::::::::::c      tt::::::::::::::t
        #                             a::::::::::aa:::a cc:::::::::::::::c        tt:::::::::::tt
        #                             aaaaaaaaaa  aaaa   cccccccccccccccc          ttttttttttt


    def refresh_inventory_capacity(self):
        logs.new_log(state=self.actor.actor_state,actor=self.actor.id, file="inventory", function="refresh_inventory_capacity", day=self.actor.simulation.time,  debug_msg= " get_product_stock "+str(self.actor.id) )

        present_capacity=0

        for product in self.main_inventory:
            present_capacity = present_capacity + self.main_inventory[product]['in_stock']

        if present_capacity > self.max_capacity:
            logs.log(warning_msg="OVERCAPACITY in actor: "+str(self.actor.id)+"  | Stock is " + str(present_capacity) + " of a max of "+ str(self.max_capacity))

        if present_capacity < 0:
                raise Exception(logs.log(warning_msg="Inventário negativo!!! no ator: {}".format(self.actor.id)))

        self.present_capacity = present_capacity
        return present_capacity

######################################################################
    def save_inventory(self):
        inventory_snapshot = {}
        for product in self.main_inventory:
            inventory_snapshot[str(product)] = self.main_inventory[product]['in_stock']

            data= {"day":self.actor.simulation.time, "inventory":inventory_snapshot}


        logs.append_line_to_file(file_path=f"{self.actor.simulation.simulation_results_folder}inventory_actor_{self.actor.id}_{self.actor.simulation.simulation_id}.csv", line=f"{data},\n")

# {1001: {'name': 'ProductA', 'id': 1001, 'initial_stock': 300000, 'safety_stock': 20000, 'composition': {'2001': 1}, 'in_stock': 153821}, 1002: {'name': 'ProductAA', 'id': 1002, 'initial_stock': 300000, 'safety_stock': 20000, 'composition': {'2001': 2}, 'in_stock': 300000}, 2001: {'id': 2001, 'in_stock': 86796}},

    def add_to_inventory(self, product, quantity):
            product, quantity = int(product), int(quantity)

            new_product=False

            present_stock = self.get_product_stock(product)
            if present_stock is False:
                present_stock = 0
                new_product = True

            logs.new_log(actor=self.actor.id, function="add_to_inventory", file="inventory", debug_msg=f"product: {product}, quantity: {quantity}, present_stock: {present_stock}")

            updated_stock = present_stock + quantity

            #quantidade inválida
            if quantity < 0:
                raise Exception("trying to add negative quantity")

            #excede a capacidade de armazenamento
            elif (self.present_capacity  + quantity) > self.max_capacity:
                logs.new_log(actor=self.actor.id, function="add_to_inventory", file="inventory", debug_msg = f"ERROR Inventory - cant insert: product: {product} -> present_capacity{self.present_capacity}+{quantity} > max_capacity {self.max_capacity} ")

                return False

            #if will not pass the max inventory
            else:
                self.set_product_inventory(product_id=product, new_quantity = updated_stock)

                self.actor.simulation.mongo_db.update_inventory_db(self.actor.id, product, updated_stock)

                #self.actor.simulation.update_global_inventory(self.actor.id ,product, quantity )                        #update the global inventory used in the dashboard
                logs.new_log(actor=self.actor.id, function="add_to_inventory", file="inventory", debug_msg=f"product added with sucess Inventory | product: {product}, present qty: {present_stock} + quantity: {quantity} -> new qty: {updated_stock}")

                return True


            # else:
            #     print("actor {}, product {}, inventory {} ".format(type(self.actor), type(product) ,self.main_inventory[product]))
            #     logs.log(debug_msg="| FUNCTION         | inventory     | inventory add_to_inventory  ERROR product does not exist !! get inventory actor: {} product: {} | inventory:{} main inventory:{}".format(self.actor, product ,self.main_inventory[product['in_stock']] ,   self.main_inventory ))
            #     return False


    def remove_from_inventory(self,  product:int, quantity:int):
        product, quantity = int(product), int(quantity)
        logs.new_log(state=self.actor.actor_state, actor=self.actor.id, file="inventory", function="remove_from_inventory", day=self.actor.simulation.time,  debug_msg=  "trying to remove_from_inventory actor:{} product:{} qty:{}".format(self.actor.id, product, quantity) )


        present_stock = self.get_product_stock(product)

        #se não existir o producto, o stock é zero
        if present_stock is False:    #present_stock = 0
            return False


        updated_stock= present_stock-quantity

        #se não tiver quantidade em stock para enviar devolve falso
        if updated_stock < 0:
            logs.new_log(state=self.actor.actor_state, actor=self.actor.id, file="inventory", function="remove_from_inventory", day=self.actor.simulation.time,  debug_msg=  " inventory     | remove_from_inventory not enough stock of product {} for odered qty of {} in actor {}. actual stock:{}".format(product, quantity, self.actor.id,product_stock) )

            return False

        #se o stock não é zero, e a quantidade é maior que o stock, envia
        else:
            self.set_product_inventory(product_id= product, new_quantity=updated_stock)
            #atualiza do stock global

            #self.actor.simulation.update_global_inventory(actor_id= actor_id, product_id= product, quantity = new_quantity )
            logs.new_log(state=self.actor.actor_state, actor=self.actor.id, file="inventory", function="remove_from_inventory", day=self.actor.simulation.time,  debug_msg=  f" inventory     | SUCCESS!!!!  removed for odered qty of {quantity} in actor {self.actor.id}. actual stock:{updated_stock}" )
            return True