import logging_management as log
log.log(debug_msg="Started transactions.py")
############################################################################################
#       Classe que contem todas as funções associadas às transações entre atores            #
#############################################################################################

# class transfer:
#     def __init__(self, sender, receiver):
#         self.sender = sender
#         self.receiver = receiver

#     def transfer(self, sender, receiver):
#         pass

def process_order(sender, receiver, quantity, product=None):
    pass





###############################################################################################
#      funções relacionadas com operações realizadas pelo actor da cadeia de valor            #
###############################################################################################
# from main import simulation_id
# from actors import ClassOrdersRecord


def receive_order(actor, quantity, product=None):
    if product== None:
        product=1
    actor.get_inventory()


def place_order(actor, quantity, product=None):
    if product== None:
        product=1
