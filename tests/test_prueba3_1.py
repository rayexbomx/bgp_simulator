import unittest
from testing_function import testingFunction
import BGP_Simulator

class Test_3_1(unittest.TestCase):
    def test_3_1(self):
        testingFunction("input_tests/prueba3_1.json","output_tests/output_test3_1.txt", "relevant_output/test_3_1.txt")
        router_to_check = '40'
        router_in_rib_in = '30.3'
        self.assertTrue(len(BGP_Simulator.routers_dict[router_to_check].rib_in[router_in_rib_in]) == 0)
        self.assertTrue(len(BGP_Simulator.routers_dict[router_to_check].rib) == 0)
        router_to_check = '50.1'
        router_in_rib_in = '30.3'
        self.assertTrue(len(BGP_Simulator.routers_dict[router_to_check].rib_in[router_in_rib_in]) == 0)
        self.assertTrue(len(BGP_Simulator.routers_dict[router_to_check].rib) == 0)
            
            

if __name__ == 'main':
    unittest.main()
