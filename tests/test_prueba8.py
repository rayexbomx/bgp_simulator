import unittest
from testing_function import testingFunction
import BGP_Simulator
import numpy as np

class Test_8(unittest.TestCase):
    def test_8(self):
        testingFunction("input_tests/prueba8.json","output_tests/output_test8.txt", "relevant_output/test_8.txt")
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

        #ROUTER 30.3 PREFIX 'A' AS PATH ['20', '10']
        router_to_check = '30.3'
        AS_PATH_check = np.array(['50'])
        self.assertTrue(np.array_equal(np.array(BGP_Simulator.routers_dict[router_to_check].rib['A']['AS_PATH'].split('_')), AS_PATH_check))

        #ROUTER 50.2 PREFIX 'A' AS PATH ['30', '20', '10']
        router_to_check = '50.2'
        AS_PATH_check = np.array(['50'])
        self.assertTrue(np.array_equal(np.array(BGP_Simulator.routers_dict[router_to_check].rib['A']['AS_PATH'].split('_')), AS_PATH_check))

        #ROUTER 60 PREFIX 'A' AS PATH ['50', '30', '20', '10']
        router_to_check = '60'
        AS_PATH_check = np.array(['50'])
        self.assertTrue(np.array_equal(np.array(BGP_Simulator.routers_dict[router_to_check].rib['A']['AS_PATH'].split('_')), AS_PATH_check))                     
            
        #ROUTER 70 NOT PREFIX 'A' IN RIB OR RIB IN
        router_to_check = '70'
        AS_PATH_check = np.array(['50'])
        self.assertTrue(np.array_equal(np.array(BGP_Simulator.routers_dict[router_to_check].rib['A']['AS_PATH'].split('_')), AS_PATH_check))    

if __name__ == 'main':
    unittest.main()
