import unittest
from testing_function import testingFunction
import BGP_Simulator
import numpy as np

class Test_7(unittest.TestCase):
    def test_7(self):
        testingFunction("input_tests/prueba7.json","output_tests/output_test7.txt", "relevant_output/test_7.txt")
        
        #WE ANNOUNCE PREFIX 'A' FROM ROUTER 20 AND ROUTER 21

        #ROUTER 10 PREFIX 'A' AS PATH ['20']
        router_to_check = '10'
        AS_PATH_check = np.array(['20'])
        self.assertTrue(np.array_equal(np.array(BGP_Simulator.routers_dict[router_to_check].rib['A']['AS_PATH'].split('_')), AS_PATH_check))

        #ROUTER 30.1 PREFIX 'A' AS PATH ['20']
        router_to_check = '30.1'
        AS_PATH_check = np.array(['20'])
        self.assertTrue(np.array_equal(np.array(BGP_Simulator.routers_dict[router_to_check].rib['A']['AS_PATH'].split('_')), AS_PATH_check))

        #ROUTER 30.2 PREFIX 'A' AS PATH ['31']
        router_to_check = '30.2'
        AS_PATH_check = np.array(['21'])
        self.assertTrue(np.array_equal(np.array(BGP_Simulator.routers_dict[router_to_check].rib['A']['AS_PATH'].split('_')), AS_PATH_check))                    
            
        #ROUTER 70 NOT PREFIX 'A' IN RIB OR RIB IN
        router_to_check = '70'
        self.assertTrue(not 'A' in BGP_Simulator.routers_dict[router_to_check].rib)
        for router_rib_in in BGP_Simulator.routers_dict[router_to_check].rib_in:
            self.assertTrue(not 'A' in BGP_Simulator.routers_dict[router_to_check].rib_in[router_rib_in])

if __name__ == 'main':
    unittest.main()
