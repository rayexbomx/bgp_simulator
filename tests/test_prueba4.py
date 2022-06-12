import unittest
from testing_function import testingFunction
import BGP_Simulator
import numpy as np

class Test_4(unittest.TestCase):
    def test_4(self):
        testingFunction("input_tests/prueba4.json","output_tests/output_test4.txt", "relevant_output/test_4.txt")
        
        #ROUTER 2 PREFIX 'A' AS PATH ['10']
        router_to_check = '20'
        AS_PATH_check = np.array(['10'])
        self.assertTrue(np.array_equal(np.array(BGP_Simulator.routers_dict[router_to_check].rib['A']['AS_PATH'].split('_')), AS_PATH_check))
        self.assertTrue(np.array_equal(np.array(BGP_Simulator.routers_dict[router_to_check].rib_in['10']['A']['AS_PATH'].split('_')), AS_PATH_check))

        #ROUTER 30.1 PREFIX 'A' AS PATH ['20', '10']
        router_to_check = '30.1'
        AS_PATH_check = np.array(['20', '10'])
        self.assertTrue(np.array_equal(np.array(BGP_Simulator.routers_dict[router_to_check].rib['A']['AS_PATH'].split('_')), AS_PATH_check))
        self.assertTrue(np.array_equal(np.array(BGP_Simulator.routers_dict[router_to_check].rib_in['20']['A']['AS_PATH'].split('_')), AS_PATH_check))
        #ROUTER 30.1 RIB IN OF 30.2 is EMPTY
        self.assertTrue(len(BGP_Simulator.routers_dict[router_to_check].rib_in['30.2']) == 0)
        #ROUTER 30.1 RIB IN OF 30.3 is EMPTY
        self.assertTrue(len(BGP_Simulator.routers_dict[router_to_check].rib_in['30.3']) == 0)

        #ROUTER 30.2 PREFIX 'A' AS PATH ['20', '10']
        router_to_check = '30.2'
        AS_PATH_check = np.array(['20', '10'])
        self.assertTrue(np.array_equal(np.array(BGP_Simulator.routers_dict[router_to_check].rib['A']['AS_PATH'].split('_')), AS_PATH_check))

        #ROUTER 30.3 PREFIX 'A' AS PATH ['20', '10']
        router_to_check = '30.3'
        AS_PATH_check = np.array(['20', '10'])
        self.assertTrue(np.array_equal(np.array(BGP_Simulator.routers_dict[router_to_check].rib['A']['AS_PATH'].split('_')), AS_PATH_check))

        #ROUTER 21 PREFIX 'A' AS PATH ['30', '20', '10']
        router_to_check = '21'
        AS_PATH_check = np.array(['30', '20', '10'])
        self.assertTrue(np.array_equal(np.array(BGP_Simulator.routers_dict[router_to_check].rib['A']['AS_PATH'].split('_')), AS_PATH_check))

        #ROUTER 50.1 PREFIX 'A' AS PATH ['30', '20', '10']
        router_to_check = '50.1'
        AS_PATH_check = np.array(['30', '20', '10'])
        self.assertTrue(np.array_equal(np.array(BGP_Simulator.routers_dict[router_to_check].rib['A']['AS_PATH'].split('_')), AS_PATH_check))

        #ROUTER 50.2 PREFIX 'A' AS PATH ['30', '20', '10']
        router_to_check = '50.2'
        AS_PATH_check = np.array(['30', '20', '10'])
        self.assertTrue(np.array_equal(np.array(BGP_Simulator.routers_dict[router_to_check].rib['A']['AS_PATH'].split('_')), AS_PATH_check))

        #ROUTER 60 PREFIX 'A' AS PATH ['50', '30', '20', '10']
        router_to_check = '60'
        AS_PATH_check = np.array(['50', '30', '20', '10'])
        self.assertTrue(np.array_equal(np.array(BGP_Simulator.routers_dict[router_to_check].rib['A']['AS_PATH'].split('_')), AS_PATH_check))                     
            
        #ROUTER 70 NOT PREFIX 'A' IN RIB OR RIB IN
        router_to_check = '70'
        self.assertTrue(not 'A' in BGP_Simulator.routers_dict[router_to_check].rib)
        self.assertTrue(not 'A' in BGP_Simulator.routers_dict[router_to_check].rib_in['50.2'])       

if __name__ == 'main':
    unittest.main()
