import unittest
from testing_function import testingFunction
import BGP_Simulator

class Test_2(unittest.TestCase):
    def test_2(self):
        testingFunction("input_tests/prueba2.json","output_tests/output_test2.txt", "relevant_output/test_2.txt")
        router_to_check = '50.1'
        router_in_rib_in = '30.3'
        self.assertTrue(len(BGP_Simulator.routers_dict[router_to_check].rib_in[router_in_rib_in]) == 0)
        self.assertTrue(len(BGP_Simulator.routers_dict[router_to_check].rib) == 0)
        router_to_check = '31'
        router_in_rib_in = '30.1'
        self.assertTrue(len(BGP_Simulator.routers_dict[router_to_check].rib_in[router_in_rib_in]) == 0)
        self.assertTrue(len(BGP_Simulator.routers_dict[router_to_check].rib) == 0)

            
            


if __name__ == 'main':
    unittest.main()
