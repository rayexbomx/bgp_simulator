import BGP_Simulator
from BGP_Simulator import Event
import json

def testingFunction(inputFilePath, outputFilePath, outputRelevantFilePath):
        input_file = open(inputFilePath)
        data = json.load(input_file)
        queue = BGP_Simulator.queue
        o_f = open(outputFilePath, 'w')
        for i in data:
            queue.put(Event(i['time'], i['action'], i['args']))
        while not queue.empty():
            next = queue.get()
            
            BGP_Simulator.callFunctions(next)

        print("\n--------------------------DUMP ALL ROUTER INFORMATION----------------------", file=o_f)
        for key in sorted(BGP_Simulator.routers_dict.keys()):
            print(" \nROUTER "+key+": \n"+BGP_Simulator.routers_dict[key].toJSON(), file=o_f)
        print("--------------------------END OF ALL ROUTER INFORMATION----------------------\n", file=o_f)


        o_f = open(outputRelevantFilePath, 'w')
        
        print("\n--------------------------DUMP ALL RELEVANT ROUTER INFORMATION----------------------", file=o_f)
        for key in sorted(BGP_Simulator.routers_dict.keys()):
            print(" \nROUTER "+key+": \n" +
              BGP_Simulator.routers_dict[key].toJSONRibAndRibIn(), file=o_f)
        print("--------------------------END OF ALL RELEVANT ROUTER INFORMATION----------------------\n", file=o_f)
        
            