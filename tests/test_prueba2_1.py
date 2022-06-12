import unittest
from testing_function import testingFunction
import BGP_Simulator

class Test_2_1(unittest.TestCase):
    def test_2_1(self):
        testingFunction("input_tests/prueba2_1.json","output_tests/output_test2_1.txt", "relevant_output/test_2_1.txt")
        for router_to_check in BGP_Simulator.routers_dict:
            self.assertTrue(len(BGP_Simulator.routers_dict[router_to_check].rib) == 0)
            for router_in_rib_in in BGP_Simulator.routers_dict[router_to_check].rib_in:
                self.assertTrue(len(BGP_Simulator.routers_dict[router_to_check].rib_in[router_in_rib_in]) == 0)


            
            


if __name__ == 'main':
    unittest.main()
