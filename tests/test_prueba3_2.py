import unittest
from testing_function import testingFunction
import BGP_Simulator

class Test_3_2(unittest.TestCase):
    def test_3_2(self):
        testingFunction("input_tests/prueba3_2.json","output_tests/output_test3_2.txt", "relevant_output/test_3_2.txt")
        for router_to_check in BGP_Simulator.routers_dict:
            self.assertTrue(len(BGP_Simulator.routers_dict[router_to_check].rib) == 0)
            for router_in_rib_in in BGP_Simulator.routers_dict[router_to_check].rib_in:
                self.assertTrue(len(BGP_Simulator.routers_dict[router_to_check].rib_in[router_in_rib_in]) == 0)
            
            


if __name__ == 'main':
    unittest.main()
