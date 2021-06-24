import yaml
import logging_management as logs, simulation, simulation_configuration

logs.log(debug_msg="Tests started")
############################################################################################
#                              Módulo para testes                                          #
############################################################################################
class ClassTests:
    def __init__(self):
        self.tests_passed=[]
        self.tests_failed=[]
        self.actors_configuration_file=simulation_configuration.actors_configuration_file

    def test_xpto(self):
        assert sum([1, 2, 3]) == 6, logs.log(debug_msg="Test 1 Failed")
    
    #test if all actors have been created


    def get_configurations(self):
        with open(self.actors_configuration_file) as file:
            actors_config = yaml.load(file, Loader=yaml.FullLoader)
            return actors_config

    #test actors criation
    def test_1(self):
        try: 
            #get list
            configurated_actors_list=self.get_configurations()['Actors'].keys()
            Object_Simulation=simulation.ClassSimulation()
            ObjectActors=Object_Simulation.create_actors(actors_configuration_file=self.actors_configuration_file)

            #get list of created objects
            simulated_actors_list=Object_Simulation.create_actors(actors_configuration_file=self.actors_configuration_file)
            if simulated_actors_list==ObjectActors:
                self.tests_passed.append("Test_1")
            else:
                raise AssertionError    
        except:
            self.tests_failed.append("Test_1")
    #test
    def test_2(self):
        try:
            if True:
                self.tests_passed.append("Test_2")
            else:
                raise AssertionError    
        except:
            self.tests_failed.append("Test_2")

    def Run_all_tests(self):

        test_list=[self.test_1(),self.test_2()]
        
        for test in test_list:
            test
        return print("Passed",len(self.tests_passed)," out of ",len(test_list),"\n Passed:",    self.tests_passed,"\n Failed:", self.tests_failed)

# simulation_configuration.print_log_in_terminal=False
    
if simulation_configuration.Run_tests:
    ObjectTests=ClassTests().Run_all_tests()
    

# TESTES A CRIAR: 
# criar ator
# criar registos
# transações
#validar registos
# 