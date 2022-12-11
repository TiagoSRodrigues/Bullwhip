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
        self.ACTORS_CONFIG_FILE=simulation_configuration.ACTORS_CONFIG_FILE

    def test_xpto(self):
        assert sum([1, 2, 3]) == 6, logs.log(debug_msg="Test 1 Failed")

    #test if all actors have been created


    def get_configurations(self):
        with open(self.ACTORS_CONFIG_FILE) as file:
            actors_config = yaml.load(file, Loader=yaml.FullLoader)
            return actors_config

    #test actors criation
    def test_1(self):
        try:
            #get list
            configurated_actors_list=self.get_configurations()['Actors'].keys()
            Object_Simulation=simulation.ClassSimulation()
            ObjectActors=Object_Simulation.create_actors(ACTORS_CONFIG_FILE=self.ACTORS_CONFIG_FILE)

            #get list of created objects
            simulated_actors_list=Object_Simulation.create_actors(ACTORS_CONFIG_FILE=self.ACTORS_CONFIG_FILE)
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

# simulation_configuration.PRINT_LOGS_IN_TERMINAL=False

if simulation_configuration.RUN_TESTS:
    ObjectTests=ClassTests().Run_all_tests()


# TESTES A CRIAR:
# criar ator
# criar registos
# transações
#validar registos
