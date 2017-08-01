#!/usr/bin/env python3

import ujson
import glob2
import sys

BASE_PATH = "data/"

def gather_diagnoses(project):
    csv = ["Project;Version;Components;Base;Default;KNN;Linear;Logistic;Tree;Forest;Xmeans;All"]
    for path in glob2.glob("{}{}/*/".format(BASE_PATH, project)):
        print(path)
        versionstr = path[:-1]
        versionstr = versionstr[versionstr.rfind('/')+1:]
        csvline = project + ";" + versionstr + ";"

        #count number of method nodes
        nodes = 0
        with open(path+"nodes.txt") as n:
            for line in n:
                obj = ujson.loads(line.rstrip())
                if obj['type'] == 'METHOD':
                    nodes += 1
        csvline += str(nodes)

        faults = []
        with open(path+"faults.txt") as f:
            faults = [int(fault.rstrip()) for fault in f]
        #print(faults)

        paths = [path+"diagnosis.txt",
                 path+"diagnosis.default.txt",
                 path+"diagnosis.knn.txt",
                 path+"diagnosis.linear.txt",
                 path+"diagnosis.logistic.txt",
                 path+"diagnosis.tree.txt",
                 path+"diagnosis.forest.txt",
                 path+"diagnosis.xmeans.txt",
                 path+"diagnosis.all.txt"]

        for p in paths:
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
                csvline += ";" + str(cd)
        #print(csvline)
        csv.append(csvline)
    with open(BASE_PATH+project+".csv", 'w') as c:
        for line in csv:
            c.write(line+'\n')


if __name__ == "__main__":
    project = sys.argv[1]
    gather_diagnoses(project)
