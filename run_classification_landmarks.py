#!/usr/bin/env python3

import sys
from valueprobes_parser import *

def create_thresholds(project, version):
    path = project_path(project, version)
    print(path)

    last_id = get_last_node_id(path)
    current_values = {}
    types = {}
    all_values = {}

    for valueprobe in iterate_valueprobes(path):
        if 'transactionName' in valueprobe:
            is_error = valueprobe['isError']
            for k, v in current_values.items():
                if k not in all_values:
                    all_values[k] = ([],[])
                all_values[k][is_error].extend(v)
            current_values.clear()
        else:
            node = valueprobe['node']
            if node not in current_values:
                current_values[node] = []
            current_values[node].append(valueprobe['value'])
            types[node] = valueprobe['t']

    print(len(all_values))

if __name__ == "__main__":
    project = sys.argv[1]
    version = sys.argv[2]
    create_thresholds(project, version)
