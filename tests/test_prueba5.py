import unittest
from testing_function import testingFunction
import numpy as np
import BGP_Simulator

class Test_5(unittest.TestCase):
    def test_5(self):
        testingFunction("input_tests/prueba5.json","output_tests/output_test5.txt", "relevant_output/test_5.txt")
        #WE DELETE PREFIX 'A' FROM ROUTER 10

        #ROUTER 10 PREFIX 'A' AS PATH ['20', '30', '31']
        router_to_check = '10'
        AS_PATH_check = np.array(['20', '30', '31'])
        self.assertTrue(np.array_equal(np.array(BGP_Simulator.routers_dict[router_to_check].rib['A']['AS_PATH'].split('_')), AS_PATH_check))

        #ROUTER 2 PREFIX 'A' AS PATH ['30', '31']
        router_to_check = '20'
        AS_PATH_check = np.array(['30', '31'])
        self.assertTrue(np.array_equal(np.array(BGP_Simulator.routers_dict[router_to_check].rib['A']['AS_PATH'].split('_')), AS_PATH_check))

        #ROUTER 30.1 PREFIX 'A' AS PATH ['31']
        router_to_check = '30.1'
        AS_PATH_check = np.array(['31'])
        self.assertTrue(np.array_equal(np.array(BGP_Simulator.routers_dict[router_to_check].rib['A']['AS_PATH'].split('_')), AS_PATH_check))

        #ROUTER 30.2 PREFIX 'A' AS PATH ['31']
        router_to_check = '30.2'
        AS_PATH_check = np.array(['31'])
        self.assertTrue(np.array_equal(np.array(BGP_Simulator.routers_dict[router_to_check].rib['A']['AS_PATH'].split('_')), AS_PATH_check))

        #ROUTER 30.3 PREFIX 'A' AS PATH ['31']
        router_to_check = '30.3'
        AS_PATH_check = np.array(['31'])
        self.assertTrue(np.array_equal(np.array(BGP_Simulator.routers_dict[router_to_check].rib['A']['AS_PATH'].split('_')), AS_PATH_check))

        #ROUTER 21 PREFIX 'A' AS PATH ['30', '31']
        router_to_check = '21'
        AS_PATH_check = np.array(['30', '31'])
        self.assertTrue(np.array_equal(np.array(BGP_Simulator.routers_dict[router_to_check].rib['A']['AS_PATH'].split('_')), AS_PATH_check))

        #ROUTER 50.1 NOT PREFIX 'A' IN RIB OR RIB IN
        router_to_check = '50.1'
        self.assertTrue(not 'A' in BGP_Simulator.routers_dict[router_to_check].rib)
        for router_rib_in in BGP_Simulator.routers_dict[router_to_check].rib_in:
            self.assertTrue(not 'A' in BGP_Simulator.routers_dict[router_to_check].rib_in[router_rib_in])

        #ROUTER 50.2 NOT PREFIX 'A' IN RIB OR RIB IN
        router_to_check = '50.2'
        self.assertTrue(not 'A' in BGP_Simulator.routers_dict[router_to_check].rib)
        for router_rib_in in BGP_Simulator.routers_dict[router_to_check].rib_in:
            self.assertTrue(not 'A' in BGP_Simulator.routers_dict[router_to_check].rib_in[router_rib_in]) 

        #ROUTER 60 NOT PREFIX 'A' IN RIB OR RIB IN
        router_to_check = '60'
        self.assertTrue(not 'A' in BGP_Simulator.routers_dict[router_to_check].rib)
        for router_rib_in in BGP_Simulator.routers_dict[router_to_check].rib_in:
            self.assertTrue(not 'A' in BGP_Simulator.routers_dict[router_to_check].rib_in[router_rib_in])                     
            
        #ROUTER 70 NOT PREFIX 'A' IN RIB OR RIB IN
        router_to_check = '70'
        self.assertTrue(not 'A' in BGP_Simulator.routers_dict[router_to_check].rib)
        for router_rib_in in BGP_Simulator.routers_dict[router_to_check].rib_in:
            self.assertTrue(not 'A' in BGP_Simulator.routers_dict[router_to_check].rib_in[router_rib_in])
            
            


if __name__ == 'main':
    unittest.main()
