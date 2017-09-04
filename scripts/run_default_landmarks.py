#!/usr/bin/env python3

import sys
import ujson
from valueprobes_parser import *

TYPE_INFO={'o': ['null', 'not null'],\
           'i': ['i == 0', 'i > 0', 'i < 0'],\
           'S': ['S == 0', 'S > 0', 'S null'],\
           'b': ['b == 0', 'b > 0', 'b < 0'],\
           's': ['s == 0', 's > 0', 's < 0'],\
           'l': ['l == 0', 'l > 0', 'l < 0'],\
           'f': ['f == 0', 'f > 0', 'f < 0'],\
           'd': ['d == 0', 'd > 0', 'd < 0'],\
           'z': ['false', 'true']}

def handle_value(value):
    if value == 0:
        return 0
    return 1 if value > 0 else 2

def get_landmark_id(landmarks, valueprobe, last_id, landmarks_file):
    probe_type = valueprobe['t']
    node_id = valueprobe['node']

    if node_id not in landmarks:
        landmarks[node_id] = [-1] * 3

    index = handle_value(valueprobe['value'])
    ret = landmarks[node_id][index]
    if ret == -1:
        # create new landmark, based on type info
        ret = last_id + 1
        landmarks[node_id][index] = ret
        d = {'parentId': node_id, 'line': -1, 'type': 'LANDMARK',\
             'id': ret, 'name': TYPE_INFO[probe_type][index]}
        landmark_str = ujson.dumps(d)
        landmarks_file.write(landmark_str+'\n')
        #print(landmark_str)
    return ret

def create_thresholds(project, version):
    path = project_path(project, version)

    landmarks_path = path + "/landmarks.default.txt"
    transactions_path = path + "/transactions.default.txt"

    last_id = get_last_node_id(path)
    landmarks = {}
    current_transaction = set()

    with open(landmarks_path, 'w') as l, open(transactions_path, 'w') as t:
        for valueprobe in iterate_valueprobes(path):
            if 'transactionName' in valueprobe:
                valueprobe['landmarks'] = list(current_transaction)
                current_transaction.clear()
                t.write(ujson.dumps(valueprobe)+'\n')
            else:
                landmark_id = get_landmark_id(landmarks, valueprobe, last_id, l)
                current_transaction.add(landmark_id)
                if landmark_id > last_id:
                    last_id = landmark_id

if __name__ == "__main__":
    project = sys.argv[1]
    version = sys.argv[2]
    create_thresholds(project, version)
