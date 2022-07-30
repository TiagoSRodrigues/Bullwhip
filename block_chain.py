


    def blockchian(self):
        simulation = self.simulation
        actors_colection= simulation.actors_collection
        block_array=[]
        for actor in actors_colection:
            get_open_orders=self.actor_stock_record.Open_Orders_Record
            actor_list=[]
            orders_data = [] 
            inventory_data=0
            for item in get_open_orders:
                orders_data.append(item[1:2])
            
            actors_array = np.array(actor_list)
            orders_array = np.array(actor_list)
            
            # a ideia é criar a array com as ordens,
            # por cada produto sumar as quantidades
            
            #criar um arrey para o ator onde adiciona [prd, qdd ordered, qdd inventario]
            
            #depois junta tudo numa matriz global com todos os atores
            
            # a quantidade de pedido que o ator X vai receber é igual ao seu indice na matrix, 
            
            #exporta uma submatriz para o caso do ator e faz a soma geral.
              
            
            for order in orders_data:
                
            inventory_data = inventory_data + self.get_product_inventory(product=item[1])

            block_array.append(item[1:2])
            # ["Time", "Product", "Qty","Client","Order_id","Status"]
            
            
            
            #adicionar aos atores
