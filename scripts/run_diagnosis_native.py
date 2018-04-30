#!/usr/bin/env python3

import sys
import subprocess
import ujson
import copy
import operator
from valueprobes_parser import *

CRITERIA = ['default',
            'knn',
            'tree',
            'forest',
            'linear',
            'logistic',
            'xmeans']

STACCATO = 'barinel/Staccato.linux.x86_64'
BARINEL = 'barinel/Barinel.linux.x86_64'

if sys.platform == "darwin":
    STACCATO = 'barinel/Staccato.macosx.x86_64'
    BARINEL = 'barinel/Barinel.macosx.x86_64'

def call(command, timeout=None):
    print(command)
    return subprocess.call(command.split(' '),timeout=timeout)

def reduce_prob(old, new):
    #return max(old,new)
    return old+new

def run_diagnosis_criterion(path, nodes, probes, transactions, criterion=None):
    probes = copy.deepcopy(probes)
    transactions = copy.deepcopy(transactions)

    matrix_path = path+"/matrix.txt"
    staccato_path = path+"/staccato.txt"
    barinel_path = path+"/barinel.txt"
    diagnosis_path = path+"/diagnosis.txt"

    landmarks = {}

    if criterion:
        matrix_path = path+"/matrix.{}.txt".format(criterion)
        staccato_path = path+"/staccato.{}.txt".format(criterion)
        barinel_path = path+"/barinel.{}.txt".format(criterion)
        diagnosis_path = path+"/diagnosis.{}.txt".format(criterion)

        landmarks_path = path+"/landmarks.{}.txt".format(criterion)
        landmarks_store = []
        parentid_counts = {}
        with open(landmarks_path) as l:
            for line in l:
                line = line.rstrip()
                obj = ujson.loads(line)
                landmarks_store.append(obj)
                parent_id = obj['parentId']
                if parent_id not in parentid_counts:
                    parentid_counts[parent_id] = 0
                parentid_counts[parent_id] += 1

        for obj in landmarks_store:
            if parentid_counts[obj['parentId']] > 1:
                parent_id = nodes[obj['parentId']]
                node_id = obj['id']
                probe_id = len(probes)
                probes.append(parent_id)
                landmarks[node_id] = probe_id

        transactions_path = path+"/transactions.{}.txt".format(criterion)
        num_components = len(probes)
        with open(transactions_path) as t:
            for index, line in enumerate(t):
                line = line.rstrip()
                obj = ujson.loads(line)
                landmark_nodes = obj['landmarks']
                transaction = transactions[index]
                length = len(transaction[0])
                if length < num_components:
                    transaction[0] = transaction[0] + [0] * (num_components - length)
                for node_id in landmark_nodes:
                    if node_id in landmarks:
                        probe_id = landmarks[node_id]
                        transaction[0][probe_id] = 1

    num_components = len(probes)
    with open(matrix_path, 'w') as m:
        for transaction in transactions:
            length = len(transaction[0])
            if length < num_components:
                transaction[0] = transaction[0] + [0] * (num_components - length)
            m.write(" ".join([str(x) for x in transaction[0]]))
            m.write(" +\n" if transaction[1] == 0 else " -\n")

    call("{} {} {} {}".format(STACCATO, str(num_components), matrix_path, staccato_path))
    call("{} {} {} {} {}".format(BARINEL,\
                                 str(num_components),\
                                 matrix_path,\
                                 staccato_path,\
                                 barinel_path))

    # parse barinel result
    probs = {}
    with open(barinel_path) as b:
        for line in b:
            line = line.rstrip()
            multiple = line.find('}')
            comps = []
            prob = 0
            if multiple == -1:
                #handle single components
                line = line.split("  ")
                comps = [int(line[0])]
                prob = float(line[1])
                pass
            else:
                comps = [int(x) for x in line[1:multiple].split(",")]
                prob = float(line[multiple+1:])

            #components are 1-indexed
            comps = [x-1 for x in comps]
            for comp in comps:
                n = probes[comp]
                if n in probs:
                    probs[n] = reduce_prob(probs[n], prob)
                else:
                    probs[n] = prob


    results = []
    for items in probs.items():
        results.append(items)
    results.sort(key=operator.itemgetter(1), reverse=True)
    with open(diagnosis_path, 'w') as d:
        for items in results:
            obj = {'nodeId': items[0], 'score': items[1]}
            d.write(ujson.dumps(obj)+"\n")
    #print(results)

def run_diagnosis(project, version):
    path = project_path(project, version)
    print(path)

    nodes = {}
    with open(path+"/nodes.txt") as n:
        for line in n:
            line = line.rstrip()
            obj = ujson.loads(line)
            if obj['type'] == 'PARAMETER':
                nodes[obj['id']] = obj['parentId']
            else:
                nodes[obj['id']] = obj['id']
            #print(obj)
    #print(nodes)

    probes = []
    with open(path+"/probes.txt") as p:
        for line in p:
            line = line.rstrip()
            obj = ujson.loads(line)
            probes.append(nodes[obj['nodeId']])
    #print(probes)

    transactions = []
    with open(path+"/transactions.txt") as t:
        for line in t:
            line = line.rstrip()
            obj = ujson.loads(line)
            transactions.append([obj['activity'], obj['isError']])
    #print(transactions)

    run_diagnosis_criterion(path, nodes, probes, transactions)
    for criterion in CRITERIA:
        run_diagnosis_criterion(path, nodes, probes, transactions, criterion)


if __name__ == "__main__":
    project = sys.argv[1]
    version = sys.argv[2]
    run_diagnosis(project, version)
