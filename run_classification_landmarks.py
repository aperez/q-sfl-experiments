#!/usr/bin/env python3

import sys
import numpy
import copy
import math
import random
import sklearn.neighbors
import sklearn.linear_model
import sklearn.tree
import sklearn.ensemble

from valueprobes_parser import *

NODE_PER_TEST_THRESHOLD = 50
RANDOM_SEED = 0

def get_landmark_id(landmarks, node_id, prediction, current_id, landmarks_file, n=2):
    if node_id not in landmarks:
        landmarks[node_id] = [-1] * n

    prediction = int(prediction)
    ret = landmarks[node_id][prediction]
    if ret == -1:
        # create new landmark, based on type info
        ret = current_id + 1
        landmarks[node_id][prediction] = ret
        d = {'parentId': node_id, 'line': -1, 'type': 'LANDMARK',\
             'id': ret, 'name': str(prediction)}
        landmark_str = ujson.dumps(d)
        landmarks_file.write(landmark_str+'\n')
        #print(landmark_str)
    return ret

def create_thresholds(project, version):
    path = project_path(project, version)
    print(path)

    last_id = get_last_node_id(path)
    current_values = {}
    types = {}
    all_values = {}
    tests = []

    random.seed(RANDOM_SEED)

    for valueprobe in iterate_valueprobes(path):
        if 'transactionName' in valueprobe:
            test_number = len(tests)
            is_error = valueprobe['isError']
            for k, v in current_values.items():
                if len(v) > NODE_PER_TEST_THRESHOLD:
                    v = random.sample(v, NODE_PER_TEST_THRESHOLD)
                if k not in all_values:
                    all_values[k] = []
                all_values[k].extend([(x, is_error, test_number) for x in v])
            current_values.clear()
            valueprobe['landmarks'] = set()
            tests.append(valueprobe)
        else:
            node = valueprobe['node']
            if node not in current_values:
                current_values[node] = []
            types[node] = valueprobe['t']
            value = valueprobe['value']
            if not math.isfinite(value):
                continue
            current_values[node].append(value)


    print(len(all_values))

    classifiers = [('knn', sklearn.neighbors.KNeighborsClassifier()),
                   ('linear', sklearn.linear_model.LinearRegression()),
                   ('logistic', sklearn.linear_model.LogisticRegression()),
                   ('tree', sklearn.tree.DecisionTreeClassifier()),
                   ('forest', sklearn.ensemble.RandomForestClassifier())]

    for classifier_name, classifier in classifiers:
        landmarks = {}
        current_id = last_id
        current_tests = copy.deepcopy(tests)

        landmarks_path = path + "/landmarks.{}.txt".format(classifier_name)
        transactions_path = path + "/transactions.{}.txt".format(classifier_name)

        with open(landmarks_path, 'w') as l, open(transactions_path, 'w') as t:

            for node, value in all_values.items():
                print("predicting node", node, "with", classifier_name)
                if len(value) < 5:
                    continue

                x = [v[0] for v in value] #value
                y = [v[1] for v in value] #is_error

                try:
                    x = numpy.array(x).reshape(-1, 1)
                    classifier.fit(x,y)

                    for v, _, tn in value:
                        prediction = classifier.predict(v)
                        landmark_id = get_landmark_id(landmarks, node, prediction[0], current_id, l)
                        if landmark_id > current_id:
                            current_id = landmark_id
                        #print(landmark_id, prediction)
                        current_tests[tn]['landmarks'].add(landmark_id)
                except:
                    pass

            #iterate current_tests, convert set to list, write to file t
            for test in current_tests:
                test['landmarks'] = list(test['landmarks'])
                t.write(ujson.dumps(test)+'\n')


if __name__ == "__main__":
    project = sys.argv[1]
    version = sys.argv[2]
    create_thresholds(project, version)
