import unittest
import BGP_Simulator
from testing_function import testingFunction


class Test_1(unittest.TestCase):
    #ROUTER 1 ANNOUNCES A PREFIX AND ROUTER 7 CANNOT GET IT
    def test_1(self):
        testingFunction("input_tests/prueba1.json","output_tests/output_test1.txt", "relevant_output/test_1.txt")
        router_to_check = '70'
        router_in_rib_in = '50.2'
        self.assertTrue(len(BGP_Simulator.routers_dict[router_to_check].rib_in[router_in_rib_in]) == 0)
        self.assertTrue(len(BGP_Simulator.routers_dict[router_to_check].rib) == 0)
            
            


if __name__ == 'main':
    unittest.main()
