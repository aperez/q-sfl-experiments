#!/usr/bin/env python3

import ujson
import glob2
import sys
import csv
import math

BASE_PATH = "data/"

def read_matrix(matrix_path):
    matrix = []
    with open(matrix_path) as m:
        for line in m:
            transaction = [x for x in line.rstrip().split(" ")]
            transaction[-1] = "1" if transaction[-1] == "-" else "0"
            transaction = [int(x) for x in transaction]
            matrix.append(transaction)
    return matrix

def calculate_metrics(path, strategy, fnodes, csvobj={}):
    matrix_path = path + "matrix.txt"
    if strategy == "Base":
        csvobj[strategy + ".Partitions"] = 0
    else:
        landmarks_path = path + "landmarks.{}.txt".format(strategy.lower())
        matrix_path = path + "matrix.{}.txt".format(strategy.lower())
        fdict = {x:0 for x in fnodes}

        with open(landmarks_path) as l:
            for line in l:
                obj = ujson.loads(line.rstrip())
                if obj['parentId'] in fnodes:
                    fdict[obj['parentId']] += 1

        csvobj[strategy + ".Partitions"] = len([1 for x,y in fdict.items() if y > 1])

def gather_diagnoses(project):
    header = ["Project", "Version"]
    strategies = ["Base", "Default", "KNN", "Linear", "Logistic",
                  "Tree", "Forest", "XMeans"]
    header.extend(strategies)
    for strategy in strategies:
        header.extend([strategy+".Partitions"])
    csvobjs = []

    for path in glob2.glob("{}{}/*/".format(BASE_PATH, project)):
        print(path)
        versionstr = path[:-1]
        versionstr = versionstr[versionstr.rfind('/')+1:]
        csvrow = {"Project": project, "Version": versionstr}

        faults = set()
        with open(path+"faults.txt") as f:
            faults = {int(fault.rstrip()) for fault in f}
        #print(faults)

        #count number of method nodes
        fnodes = set(faults)

        nodes = 0
        with open(path+"nodes.txt") as n:
            for line in n:
                obj = ujson.loads(line.rstrip())
                if obj['type'] == 'METHOD':
                    nodes += 1
                if obj['parentId'] in fnodes:
                    fnodes.add(obj['id'])
        #print(fnodes)

        #print(faults)

        paths = [("Base", path+"diagnosis.txt"),
                 ("Default",path+"diagnosis.default.txt"),
                 ("KNN", path+"diagnosis.knn.txt"),
                 ("Linear", path+"diagnosis.linear.txt"),
                 ("Logistic", path+"diagnosis.logistic.txt"),
                 ("Tree", path+"diagnosis.tree.txt"),
                 ("Forest", path+"diagnosis.forest.txt"),
                 ("XMeans", path+"diagnosis.xmeans.txt"),
                 ]

        for name, p in paths:
            with open(p) as d:
                cd = 0
                counter = 1
                score = 0
                found = False

                for line in d:
                    obj = ujson.loads(line.rstrip())
                    if obj['score'] == score:
                        counter += 1
                    else:
                        if found:
                            cd += (counter-1)/2
                            counter = 0
                            break
                        cd += counter
                        counter = 1
                        score = obj['score']


                    if obj['nodeId'] in faults:
                        found = True
                if counter != 0:
                    cd += counter
                if not found:
                    cd = cd + (nodes - cd) / 2
                #print("cd", cd)
                csvrow[name] = cd

        #print(csvline)
        for strategy in strategies:
            calculate_metrics(path, strategy, fnodes, csvrow)
        csvobjs.append(csvrow)

    with open(BASE_PATH+project+".csv", 'w') as c:
        w = csv.DictWriter(c, header, extrasaction='ignore')
        w.writeheader()
        for csvrow in csvobjs:
            w.writerow(csvrow)


if __name__ == "__main__":
    project = sys.argv[1]
    gather_diagnoses(project)
