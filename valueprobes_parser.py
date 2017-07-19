import sys
import ujson

BASE_PATH="../results/data"

def project_path(project, version, base=BASE_PATH):
    return "{}/{}/{}".format(base, project, version)

def get_last_node_id(path):
    nodes_path = path + "/nodes.txt"
    last_id = 0
    with open(nodes_path, 'r') as f:
        for line in f:
            line = line.rstrip()
            d = ujson.loads(line)
            if 'id' in d and d['id'] > last_id:
                last_id = d['id']
    return last_id

def iterate_valueprobes(path):
    valueprobes_path = path + "/valueprobes.txt"

    with open(valueprobes_path, 'r') as f:
        for line in f:
            line = line.rstrip()
            d = {}
            try:
                d = ujson.loads(line)
                yield d
            except:
                continue
