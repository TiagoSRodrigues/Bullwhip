from logging_management import *
log(debug_msg="Tests started")
############################################################################################
#     Módulo para testes            #
#############################################################################################
def tests():
    assert sum([1, 2, 3]) == 6, log(debug_msg="Test 1 Failed")

    
if __name__ == "__main__":
    tests()
    log(debug_msg="Everything passed")

# TESTES A CRIAR: 
# criar ator
# criar registos
# transações
#validar registos
# 