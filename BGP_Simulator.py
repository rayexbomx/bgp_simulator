import json
import sys
from queue import PriorityQueue
import argparse
import traceback
import random
import time

from matplotlib.pyplot import new_figure_manager

start = time.time()
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# CREATING CLASSES

class Router:
    def __init__(self):
        self.links = {}  # Links between each AS router
        self.relationship = {}
        self.local_pref = {}  # local_pref betweet routers
        self.rib = {}
        self.local_rib = {}  # Own's local RIB
        self.rib_in = {}  # Dictionary of outer AS router RIBS
        self.sent_to = {}
        self.MRAI = {"configuration": {}, "per_session": {}, "per_prefix": {}}
        self.routerDown = False

    def toJSON(self):
        json_str = json.dumps(self, default=lambda o: o.__dict__,
                              sort_keys=False, indent=4)
        return json_str

    def toJSONRibAndRibIn(self):
        tmp = {'RIB ->': {}, 'RIB_IN ->': {}}
        for router in self.rib_in:
            for prefix in self.rib_in[router]:
                tmp["RIB_IN ->"] = {router: (prefix, list(
                    self.rib_in[router][prefix]['AS_PATH'].split("_")))}
        for prefix in self.rib:
            if 'AS_PATH' in self.rib[prefix]:
                tmp["RIB ->"] = {prefix: list(self.rib[prefix]
                                              ['AS_PATH'].split("_"))}
            else:
                tmp["RIB ->"] = {prefix: 'SELF ANNOUNCED'}
        return json.dumps(tmp, default=lambda o: o.__dict__,
                          sort_keys=False, indent=4)


class Event:
    def __init__(self, time, action, args):
        self.time = time  # VIRTUAL TIME OF EVENT
        self.action = action  # ACTION INSTRUCTION
        self.args = args  # ARGUMENTS

    def __eq__(self, Event: object) -> bool:
        return self.time == Event.time

    def __lt__(self, Event: object) -> bool:
        return self.time < Event.time

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=False, indent=4)


queue = PriorityQueue()
routers_dict = dict()


def checkRib(tmp):
    router = tmp.args["router"]
    check_rib_in = dict()
    for prefix in routers_dict[router].local_rib:
        if not prefix in routers_dict[router].rib:
            check_rib_in[prefix] = (
                True, [routers_dict[router].local_rib[prefix]])
        elif 'AS_PATH' in routers_dict[router].rib[prefix]:
            check_rib_in[prefix] = (
                True, [routers_dict[router].local_rib[prefix]])
            # CHECKEAR QUE SI ESTA EN LA RIB PERO CON AS PATH, VAS A PREFERIR SIEMPRE EL TUYO.
    for router_rib_in in routers_dict[router].rib_in:
        for prefix in routers_dict[router].rib_in[router_rib_in]:
            if prefix in routers_dict[router].local_rib:
                pass
            else:
                if not prefix in check_rib_in:
                    check_rib_in[prefix] = (
                        True, routers_dict[router].rib_in[router_rib_in][prefix], router_rib_in)
                else:
                    if check_rib_in[prefix][1]["local_pref"] < routers_dict[router].rib_in[router_rib_in][prefix]["local_pref"]:
                        check_rib_in[prefix] = (
                            True, routers_dict[router].rib_in[router_rib_in][prefix], router_rib_in)
                    elif check_rib_in[prefix][1]["local_pref"] == routers_dict[router].rib_in[router_rib_in][prefix]["local_pref"]:
                        if len(check_rib_in[prefix][1]["AS_PATH"].split("_")) > len(routers_dict[router].rib_in[router_rib_in][prefix]["AS_PATH"].split("_")):
                            check_rib_in[prefix] = (
                                True, routers_dict[router].rib_in[router_rib_in][prefix], router_rib_in)
                        elif len(check_rib_in[prefix][1]["AS_PATH"].split("_")) == len(routers_dict[router].rib_in[router_rib_in][prefix]["AS_PATH"].split("_")):
                            if routers_dict[router].relationship[check_rib_in[prefix][2]] == "ibgp" and routers_dict[router].relationship[router_rib_in] != "ibgp":
                                check_rib_in[prefix] = (
                                    True, routers_dict[router].rib_in[router_rib_in][prefix], router_rib_in)
    for prefix in check_rib_in:
        if prefix in routers_dict[router].local_rib:
            if prefix in routers_dict[router].rib:
                if 'AS_PATH' in routers_dict[router].rib[prefix]:
                    if prefix in routers_dict[router].sent_to:
                        for sent_to in routers_dict[router].sent_to[prefix][AS_PATH]:
                            event_tmp = Event(
                                tmp.time + 1, "MRAIF", args={"s": router, "dest": sent_to, "P": prefix, 'AS_PATH': AS_PATH, "withraw": True})
                            queue.put(event_tmp)
            for send_to in routers_dict[router].links:
                if routers_dict[router].links[send_to]:
                    event_tmp = Event(tmp.time + 1, "MRAIF", args={"s": router, "dest": send_to, "P": prefix, "AS_PATH": router.split(".")[
                                      0], "relationship": routers_dict[send_to].relationship[router], "sender": "local", 'withraw': False})
                    queue.put(event_tmp)
                    routers_dict[router].rib[prefix] = {"time": tmp.time}
        else:
            if prefix in routers_dict[router].rib:
                if "AS_PATH" in routers_dict[router].rib[prefix]:
                    if check_rib_in[prefix][1]["AS_PATH"] != routers_dict[router].rib[prefix]["AS_PATH"]:
                        time = tmp.time
                        AS_PATH = check_rib_in[prefix][1]["AS_PATH"]
                        relationship = check_rib_in[prefix][1]["relationship"]
                        local_pref = check_rib_in[prefix][1]["local_pref"]
                        for send_to in routers_dict[router].links:
                            if routers_dict[router].links[send_to] and check_rib_in[prefix][2] != send_to:
                                event_tmp = Event(tmp.time + 1, "MRAIF", args={"s": router, "dest": send_to, "P": prefix, "AS_PATH": AS_PATH,
                                                                               "relationship": routers_dict[send_to].relationship[router], "sender": check_rib_in[prefix][2], "withraw": False})
                                queue.put(event_tmp)
                        routers_dict[router].rib[prefix] = {
                            "time": time, "AS_PATH": AS_PATH, "relationship": relationship, "local_pref": local_pref, "sender": check_rib_in[prefix][2]}
                        for prefix in routers_dict[router].sent_to:
                            if not prefix in routers_dict[router].local_rib:
                                for AS_PATH in list(routers_dict[router].sent_to[prefix]):
                                    if prefix in routers_dict[router].rib:
                                        if 'AS_PATH' in routers_dict[router].rib[prefix]:
                                            if AS_PATH != routers_dict[router].rib[prefix]['AS_PATH']:
                                                for sent_to in routers_dict[router].sent_to[prefix][AS_PATH]:
                                                    event_tmp = Event(
                                                        tmp.time + 1, "MRAIF", args={"s": router, "dest": sent_to, "P": prefix, 'AS_PATH': AS_PATH, "withraw": True})
                                                    queue.put(event_tmp)
                                                routers_dict[router].sent_to[prefix].pop(
                                                    AS_PATH)
            else:
                time = tmp.time
                AS_PATH = check_rib_in[prefix][1]["AS_PATH"]
                local_pref = check_rib_in[prefix][1]["local_pref"]
                relationship = check_rib_in[prefix][1]["relationship"]
                routers_dict[router].rib[prefix] = {
                    "time": time, "AS_PATH": AS_PATH, "relationship": relationship, "local_pref": local_pref, "sender": check_rib_in[prefix][2]}
                for send_to in routers_dict[router].links:
                    if routers_dict[router].links[send_to] and check_rib_in[prefix][2] != send_to:
                        event_tmp = Event(tmp.time + 1, "MRAIF", args={"s": router, "dest": send_to, "P": prefix, "AS_PATH": AS_PATH,
                                                                       "relationship": routers_dict[send_to].relationship[router], "sender": check_rib_in[prefix][2], "withraw": False})
                        queue.put(event_tmp)

    for prefix in list(routers_dict[router].rib):
        if not prefix in check_rib_in and not prefix in routers_dict[router].local_rib:
            routers_dict[router].rib.pop(prefix)
            if prefix in routers_dict[router].sent_to:
                for AS_PATH in list(routers_dict[router].sent_to[prefix]):
                    for sent_to in routers_dict[router].sent_to[prefix][AS_PATH]:
                        event_tmp = Event(
                            tmp.time, "MRAIF", args={"s": router, "dest": sent_to, 'AS_PATH': AS_PATH, "P": prefix, "withraw": True})
                        queue.put(event_tmp)
                    routers_dict[router].sent_to[prefix].pop(AS_PATH)

"""TODO"""
def MRAIfunction(temp):
    source = temp.args['s']
    neighbor = temp.args["dest"]
    prefix = temp.args["P"]
    if not temp.args["withraw"]:
        AS_PATH = temp.args["AS_PATH"]
        sender = temp.args["sender"]
        relationship = temp.args["relationship"]
        if neighbor in routers_dict[source].MRAI['configuration']:
            if routers_dict[source].MRAI['configuration'][neighbor]['type'] == 'per_session':
                print()
            if routers_dict[source].MRAI['configuration'][neighbor]['type'] == 'per_prefix':
                print()
        else:

            event_tmp = Event(temp.time + 2, "SBR", args={"s": source, "nb": neighbor, "P": prefix, "AS_PATH": AS_PATH,
                                                          "relationship": relationship, "sender": sender, "withraw": False})
            queue.put(event_tmp)

    elif temp.args["withraw"]:
        if neighbor in routers_dict[source].MRAI['configuration']:
            if routers_dict[source].MRAI['configuration'][neighbor]['type'] == 'per_session':
               print()
            if routers_dict[source].MRAI['configuration'][neighbor]['type'] == 'per_prefix':
                print()
        else:
            event_tmp = Event(temp.time + 1, "SBR", args={
                              "s": source, "P": prefix, "nb": neighbor, 'AS_PATH': temp.args["AS_PATH"], "withraw": True})
            queue.put(event_tmp)

"""TODO"""
def sendMRAI(tmp):
    source = tmp.args["source"]
    destination = tmp.args['destination']
    prefix = tmp.args['P']
    if routers_dict[source].MRAI['configuration'][destination]['type'] == 'per_session':
        print() 
    elif routers_dict[source].MRAI['configuration'][destination]['type'] == 'per_prefix':
        print()


def MRAIconfiguration(tmp):
    router_1 = tmp.args['router_1']
    router_2 = tmp.args['router_2']
    typeOfMRAI = tmp.args['type']
    if typeOfMRAI == 'per_session':
        random_number = random.randrange(int(tmp.args['timer']))
        routers_dict[router_1].MRAI['configuration'][router_2] = {
            'type': 'per_session', 'timer': tmp.args['timer'], 'threshold': random_number, 'on': False, 'start_time': 0}
        routers_dict[router_1].MRAI['per_session'][router_2] = {}
        routers_dict[router_2].MRAI['configuration'][router_1] = {
            'type': 'per_session', 'timer': tmp.args['timer'], 'threshold': random_number, 'on': False, 'start_time': 0}
        routers_dict[router_2].MRAI['per_session'][router_1] = {}

    elif typeOfMRAI == 'per_prefix':
        random_number = random.randrange(int(tmp.args['timer']))
        routers_dict[router_1].MRAI['configuration'][router_2] = {
            'type': 'per_prefix', 'timer': tmp.args['timer'], 'threshold': random_number, 'on': False, 'prefix_timers': {}, 'start_time': 0}
        routers_dict[router_2].MRAI['configuration'][router_1] = {
            'type': 'per_prefix', 'timer': tmp.args['timer'], 'threshold': random_number, 'on': False, 'prefix_timers': {}, 'start_time': 0}


def sendBestRoute(tmp):
    source = tmp.args["s"]
    prefix = tmp.args["P"]
    nb = tmp.args["nb"]

    if not tmp.args["withraw"]:
        AS_PATH = tmp.args["AS_PATH"]
        relationship = tmp.args["relationship"]
        if prefix in routers_dict[source].local_rib:
            event_tmp = Event(tmp.time + 1, "U", args={"s": source, "dest": nb, "P": prefix,
                                                       "AS_PATH": AS_PATH, "relationship": relationship})
            queue.put(event_tmp)
            if not prefix in routers_dict[source].sent_to or not AS_PATH in routers_dict[source].sent_to[prefix]:
                routers_dict[source].sent_to[prefix] = dict()
                routers_dict[source].sent_to[prefix][AS_PATH] = [nb]
            else:
                routers_dict[source].sent_to[prefix][AS_PATH] = [nb]
        elif tmp.args['sender'] == 'local':
            pass
        else:
            sender = tmp.args["sender"]
            send_to = {}
            if sender != 'local':
                if routers_dict[source].relationship[sender] != 'ibgp' and routers_dict[source].relationship[nb] == 'p2c':
                    send_to = {"s": source, "dest": nb, "P": prefix, "AS_PATH": source.split(
                        ".")[0] + '_' + AS_PATH, "relationship": relationship}
                elif routers_dict[source].relationship[sender] == 'p2c' and routers_dict[source].relationship[nb] == 'c2p':
                    send_to = {"s": source, "dest": nb, "P": prefix, "AS_PATH": source.split(
                        ".")[0] + '_' + AS_PATH, "relationship": relationship}
                elif routers_dict[source].relationship[sender] == 'p2c' and routers_dict[source].relationship[nb] == 'p2p':
                    send_to = {"s": source, "dest": nb, "P": prefix, "AS_PATH": source.split(
                        ".")[0] + '_' + AS_PATH, "relationship": relationship}
                elif routers_dict[source].relationship[sender] == 'ibgp' and routers_dict[source].relationship[nb] != 'ibgp':
                    if prefix in routers_dict[source].rib:
                        if routers_dict[source].rib[prefix]["relationship"] == 'p2c':
                            send_to = {"s": source, "dest": nb, "P": prefix, "AS_PATH": source.split(
                                ".")[0] + '_' + AS_PATH, "relationship": relationship}
                        elif routers_dict[source].rib[prefix]["relationship"] == 'ibgp':
                            send_to = {"s": source, "dest": nb, "P": prefix, "AS_PATH": AS_PATH,
                                       "relationship": relationship}
                        elif routers_dict[source].rib[prefix]["relationship"] == 'c2p' and routers_dict[source].relationship[nb] == 'p2c':
                            send_to = {"s": source, "dest": nb, "P": prefix, "AS_PATH": source.split(
                                ".")[0] + '_' + AS_PATH, "relationship": relationship}
                        elif routers_dict[source].rib[prefix]["relationship"] == 'p2p' and routers_dict[source].relationship[nb] == 'p2c':
                            send_to = {"s": source, "dest": nb, "P": prefix, "AS_PATH": source.split(
                                ".")[0] + '_' + AS_PATH, "relationship": relationship}
                elif routers_dict[source].relationship[sender] != 'ibgp' and routers_dict[source].relationship[nb] == 'ibgp':
                    send_to = {"s": source, "dest": nb, "P": prefix, "AS_PATH":  AS_PATH,
                               "relationship": routers_dict[source].rib[prefix]["relationship"], 'local_pref': routers_dict[source].rib_in[sender][prefix]["local_pref"]}
                elif routers_dict[source].relationship[sender] == 'ibgp' and routers_dict[source].relationship[nb] == 'ibgp':
                    pass
                elif prefix in routers_dict[source].sent_to:
                    if nb in routers_dict[source].sent_to[prefix]:
                        event_tmp = Event(
                            tmp.time, "W", args={"s": source, "dest": nb, 'AS_PATH': routers_dict[source].sent_to[prefix][nb][1], "P": prefix})
                        queue.put(event_tmp)
                        routers_dict[source].sent_to[prefix].pop(nb)
                if len(send_to.keys()) != 0:
                    event_tmp = Event(tmp.time + 1, "U", args=send_to)
                    queue.put(event_tmp)
                    if not prefix in routers_dict[source].sent_to or not AS_PATH in routers_dict[source].sent_to[prefix]:
                        routers_dict[source].sent_to[prefix] = dict()
                        routers_dict[source].sent_to[prefix][AS_PATH] = [nb]
                    else:
                        routers_dict[source].sent_to[prefix][AS_PATH].append(
                            nb)
    elif tmp.args['withraw']:
        event_tmp = Event(
            tmp.time + 1, "W", args={"s": source, "dest": nb, "P": prefix, "AS_PATH": tmp.args['AS_PATH']})
        queue.put(event_tmp)


def update(tmp):
    time = tmp.time
    source = tmp.args["s"]
    destination = tmp.args["dest"]
    prefix = tmp.args["P"]
    tmp.args.update({'time': time})
    try:
        routers_dict[destination].rib_in[source][prefix] = tmp.args
        if not 'local_pref' in tmp.args:
            try:
                routers_dict[destination].rib_in[source][prefix]['local_pref'] = routers_dict[destination].local_pref[source]
            except:
                routers_dict[destination].rib_in[source][prefix]['local_pref'] = 1000
        else:
            tmp.args['local_pref']
    except:
        pass
    tmp.args = {"router": destination}
    event_tmp = Event(tmp.time, "CR", args=tmp.args)
    queue.put(event_tmp)


def withdraw(tmp):
    source = tmp.args["s"]
    destination = tmp.args["dest"]
    prefix = tmp.args["P"]
    if source in routers_dict[destination].rib_in:
        if prefix in routers_dict[destination].rib_in[source]:
            routers_dict[destination].rib_in[source].pop(prefix)
    event_tmp = Event(tmp.time + 5, "CR", args={"router": destination})
    queue.put(event_tmp)


def generateAnnouncement(tmp):
    router = tmp.args["generator"]
    prefix = tmp.args["P"]
    routers_dict[router].local_rib[prefix] = {
        "time": tmp.time, "relationship": "", "local_pref": tmp.args["local_pref"], "AS_PATH": ""}
    event_tmp = Event(
        tmp.time, "CR", args={"router": router})
    queue.put(event_tmp)


def deleteAnnouncement(tmp):
    router = tmp.args["router"]
    prefix = tmp.args["P"]
    routers_dict[router].local_rib.pop(prefix)
    event_tmp = Event(tmp.time, "CR", args={"router": router})
    queue.put(event_tmp)


def linkDown(tmp):
    router_1 = tmp.args["router_1"]
    router_2 = tmp.args["router_2"]
    routers_dict[router_1].links[router_2] = False
    routers_dict[router_2].links[router_1] = False
    event_tmp_1 = Event(tmp.time + 1, "LDD",
                        args={"router_1": router_1, "router_2": router_2})
    event_tmp_2 = Event(tmp.time + 1, "LDD",
                        args={"router_1": router_2, "router_2": router_1})
    queue.put(event_tmp_1)
    queue.put(event_tmp_2)


def linkDownDetection(tmp):
    router_1 = tmp.args["router_1"]
    router_2 = tmp.args["router_2"]
    routers_dict[router_1].rib_in.pop(router_2)
    event_tmp_1 = Event(tmp.time, "CR", args={"router": router_1})
    queue.put(event_tmp_1)


def linkUp(tmp):
    router_1 = tmp.args["router_1"]
    router_2 = tmp.args["router_2"]
    try:
        relationship = tmp.args["relationship"]
        if relationship != "ibgp":
            relationship_2 = relationship[::-1]
        else:
            relationship_2 = relationship
        if "local_pref_1" in tmp.args:
            local_pref_1 = tmp.args["local_pref_1"]
        else:
            if relationship == 'p2c':
                local_pref_1 = 120
            elif relationship == 'c2p':
                local_pref_1 = 100
            elif relationship == 'p2p':
                local_pref_1 = 110
        if "local_pref_2" in tmp.args:
            local_pref_2 = tmp.args["local_pref_2"]
        else:
            if relationship_2 == 'p2c':
                local_pref_2 = 120
            elif relationship_2 == 'c2p':
                local_pref_2 = 100
            elif relationship_2 == 'p2p':
                local_pref_2 = 110
        routers_dict[router_1].relationship[router_2] = relationship
        routers_dict[router_2].relationship[router_1] = relationship_2
        if relationship != "ibgp":
            routers_dict[router_1].local_pref[router_2] = local_pref_1
            routers_dict[router_2].local_pref[router_1] = local_pref_2
        routers_dict[router_1].links[router_2] = True
        routers_dict[router_2].links[router_1] = True
        routers_dict[router_1].rib_in[router_2] = dict()
        routers_dict[router_2].rib_in[router_1] = dict()
        event_tmp_1 = Event(tmp.time, "CR", args={"router": router_1})
        event_tmp_2 = Event(tmp.time, "CR", args={"router": router_2})
        queue.put(event_tmp_1)
        queue.put(event_tmp_2)
    except:
        routers_dict[router_1].links[router_2] = True
        routers_dict[router_2].links[router_1] = True
        routers_dict[router_1].rib_in[router_2] = dict()
        routers_dict[router_2].rib_in[router_1] = dict()
        for prefix in routers_dict[router_1].rib:
            if not prefix in routers_dict[router_1].local_rib:
                event_tmp = Event(tmp.time, "SBR", args={"s": router_1, "nb": router_2, "P": prefix, "AS_PATH": routers_dict[router_1].rib[prefix]['AS_PATH'],
                                                         "relationship": routers_dict[router_2].relationship[router_1], "sender": routers_dict[router_1].rib[prefix]['sender'], "withraw": False})
                queue.put(event_tmp)
            else:
                event_tmp = Event(tmp.time + 1, "MRAIF", args={"s": router_1, "nb": router_2, "P": prefix, "AS_PATH": router_1.split(".")[
                    0], "relationship": routers_dict[router_2].relationship[router_1], "sender": "local", 'withraw': False})
                queue.put(event_tmp)
        for prefix in routers_dict[router_2].rib:
            if not prefix in routers_dict[router_2].local_rib:
                event_tmp = Event(tmp.time, "SBR", args={"s": router_2, "nb": router_1, "P": prefix, "AS_PATH": routers_dict[router_2].rib[prefix]['AS_PATH'],
                                                         "relationship": routers_dict[router_1].relationship[router_2], "sender": routers_dict[router_2].rib[prefix]['sender'], "withraw": False})
                queue.put(event_tmp)
            else:
                event_tmp = Event(tmp.time + 1, "MRAIF", args={"s": router_2, "nb": router_1, "P": prefix, "AS_PATH": router_2.split(".")[
                    0], "relationship": routers_dict[router_1].relationship[router_2], "sender": "local", 'withraw': False})
                queue.put(event_tmp)


def routerDown(tmp):
    router = tmp.args["router_id"]
    routers_dict[router].routerDown = True
    for link in routers_dict[router].links:
        for prefix in routers_dict[router].sent_to:
            if link in routers_dict[router].sent_to[prefix]:
                routers_dict[router].sent_to[prefix].pop(link)
            if prefix in routers_dict[link].sent_to:
                if router in routers_dict[link].sent_to[prefix]:
                    routers_dict[router].sent_to[prefix].pop(router)
        event_tmp = Event(tmp.time + 1, "LD",
                          args={"router_1": router, "router_2": link})
        queue.put(event_tmp)


def routerUp(tmp):
    router = tmp.args["router_id"]
    if router in routers_dict:
        routers_dict[router].routerDown = False
        for link in routers_dict[router].links:
            if not routers_dict[link].routerDown:
                event_tmp = Event(tmp.time + 1, "LU", args={
                    "router_1": router, 'router_2': link})
                queue.put(event_tmp)
    else:
        routers_dict[tmp.args['router_id']] = Router()


def dumpRouterInformation(args):
    print("\n\n--------------Router information--------------- \nROUTER " +
          args['router_id'] + ': \n' + routers_dict[args['router_id']].toJSON() + '\n--------------Router information---------------\n\n', file=o_f)


def dumpAllRouterInformation():
    print("\n--------------------------DUMP ALL ROUTER INFORMATION----------------------", file=o_f)
    for key in sorted(routers_dict.keys()):
        print(" \nROUTER "+key+": \n"+routers_dict[key].toJSON(), file=o_f)
    print("--------------------------END OF ALL ROUTER INFORMATION----------------------\n", file=o_f)


def printRelevantInformation():
    print("\n--------------------------DUMP ALL RELEVANT ROUTER INFORMATION----------------------", file=o_f)
    for key in sorted(routers_dict.keys()):
        print(" \nROUTER "+key+": \n" +
              routers_dict[key].toJSONRibAndRibIn(), file=o_f)
    print("--------------------------END OF ALL RELEVANT ROUTER INFORMATION----------------------\n", file=o_f)



def callFunctions(tmp):
    try:
        if tmp.action == 'U':
            update(tmp)
        elif tmp.action == 'SBR':
            sendBestRoute(tmp)
        elif tmp.action == 'GA':
            # ARGS MUST BE: args: {"p": "1.1.1.0/24", "generator": "1.1", "ap": "router_1"}
            generateAnnouncement(tmp)
        elif tmp.action == 'RA':
            deleteAnnouncement(tmp)
        elif tmp.action == 'LD':
            linkDown(tmp)
        elif tmp.action == 'CR':
            checkRib(tmp)
        elif tmp.action == 'LDD':
            linkDownDetection(tmp)
        elif tmp.action == 'LU':
            # ARGS MUST BE: args: {router_1 : "ROUTER_1_ID" ; router_2 : "ROUTER_2_ID"}
            linkUp(tmp)
        elif tmp.action == 'RD':
            routerDown(tmp)  # ARGS MUST BE: {router_id : "DOWN_ROUTER_ID"}
        elif tmp.action == 'RU':
            routerUp(tmp)  # ARGS MUST BE: args: {router_id : "NEW_ROUTER_ID"}
        elif tmp.action == 'DR':
            # ARGS MUST BE: args: {router_id : "ROUTER_ID"}
            dumpRouterInformation(tmp.args)
        elif tmp.action == 'DAR':
            dumpAllRouterInformation()  # NO ARGS
        elif tmp.action == 'W':
            withdraw(tmp)
        elif tmp.action == 'PRI':
            printRelevantInformation()
        elif tmp.action == 'MRAIF':
            MRAIfunction(tmp)
        elif tmp.action == 'SMRAI':
            sendMRAI(tmp)
        elif tmp.action == 'CMRAI':
            MRAIconfiguration(tmp)
        else:
            print(bcolors.FAIL+"Error: Wrong action \"" +
                  tmp.action + "\" check -help" + bcolors.ENDC)
    except Exception as e:
        print(bcolors.FAIL + 'Error processing action ' + tmp.action + ' in time ' +
              str(tmp.time) + ' error caused by: \n' + str(traceback.format_exc()) + bcolors.ENDC)


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(
        description='Plot mean rate of different mechanisms')
    # get mechanism list, separated by commas
    argparser.add_argument('-i', '--input_filename', type=str,
                           help='Input filename,e.g., input.txt', required=True)
    # get input filename
    argparser.add_argument('-o', '--output_filename', type=str,
                           help='Output filename,e.g., output.txt', required=True)
    parsed_args = argparser.parse_args()
    INPUT_FILE = parsed_args.input_filename
    OUTPUT_FILE = parsed_args.output_filename
    # ERROR: OPENING INPUT FILE
    try:
        i_f = open(INPUT_FILE)
    except Exception as e:
        print('Error: Failed to open file.')
        sys.exit()
    # ERROR: CREATING OUTPUT FILE
    try:
        o_f = open(OUTPUT_FILE, 'w')
    except Exception as e:
        print('Error: Failed to create output.txt file.')
        sys.exit()
        # CREATING QUEUE

    data = json.load(i_f)

    # SET JSON INTO EVENT OBJECTS
    
    for i in data:
        tmp = Event(i['time'], i['action'], i['args'])
        queue.put(tmp)
    while not queue.empty():
        next = queue.get()
        try:
            print(next.toJSON(), file=o_f)
            callFunctions(next)
        except Exception as e:
            print("Error: internal error while processing event " + next['action'] + " in relative time " + next['time'] + " with arguments: " + next['args'])
    
    dumpAllRouterInformation()
    end = time.time()
    print("Execution time: " + str(end - start))
