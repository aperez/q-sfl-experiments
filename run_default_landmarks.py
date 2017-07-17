#!/usr/bin/env python3

import sys
import json

BASE_PATH="../results/data"
TYPE_INFO={'o': ['null', 'not null'],\
           'i': ['i == 0', 'i > 0', 'i < 0'],\
           'S': ['S == 0', 'S > 0', 'S null'],\
           'b': ['b == 0', 'b > 0', 'b < 0'],\
           's': ['s == 0', 's > 0', 's < 0'],\
           'l': ['l == 0', 'l > 0', 'l < 0'],\
           'f': ['f == 0', 'f > 0', 'f < 0'],\
           'd': ['d == 0', 'd > 0', 'd < 0'],\
           'z': ['false', 'true']}

def project_path(project, version, base=BASE_PATH):
    return "{}/{}/{}".format(base, project, version)

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
        landmark_str = json.dumps(d)
        landmarks_file.write(landmark_str+'\n')
        #print(landmark_str)
    return ret

def create_thresholds(project, version):
    path = project_path(project, version)
    print(path)

    nodes_path = path + "/nodes.txt"
    last_id = 0
    with open(nodes_path, 'r') as f:
        for line in f:
            line = line.rstrip()
            d = json.loads(line)
            if 'id' in d and d['id'] > last_id:
                last_id = d['id']

    valueprobes_path = path + "/valueprobes.txt"
    landmarks_path = path + "/landmarks.default.txt"
    transactions_path = path + "/transactions.default.txt"

    landmarks = {}
    current_transaction = set()
    with open(valueprobes_path, 'r') as f, open(landmarks_path, 'w') as l,\
            open(transactions_path, 'w') as t:
        for line in f:
            line = line.rstrip()
            d = json.loads(line)
            if 'transactionName' in d:
                d['landmarks'] = list(current_transaction)
                current_transaction.clear()
                t.write(json.dumps(d)+'\n')
            else:
                landmark_id = get_landmark_id(landmarks, d, last_id, l)
                current_transaction.add(landmark_id)
                if landmark_id > last_id:
                    last_id = landmark_id

if __name__ == "__main__":
    project = sys.argv[1]
    version = sys.argv[2]
    create_thresholds(project, version)
