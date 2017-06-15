#!/usr/bin/env python3

import os
import sys
import subprocess
import yaml

exp = yaml.load(open("experiment.yml", 'r'))

def call(command):
    print(command)
    subprocess.call(command.split(' '))

def project_path(project, version, base=exp['base-path']):
    return "{}/{}/{}".format(base, project, version)

def export(project, version):
    path = project_path(project, version)
    os.chdir(path)

    data_path = project_path(project, version, exp['data-path'])
    call("mkdir -p {}".format(data_path))

    #copy files
    for f in ["nodes.txt", "probes.txt", "transactions.txt"]:
        call("cp {} {}".format(f, data_path))

    return True

def run(project, version):
    path = project_path(project, version)
    os.chdir(path)

    with open("cp.test.txt", 'r') as f:
        bootsrapper = exp['bootstrapper']['jar']
        junit = exp['d4j']['path'] + exp['d4j']['junit']
        classpath = ":".join([bootsrapper, junit, f.readline().rstrip()])
        agent_options = "".join(["{", exp['instrumenter']['options'].replace(" ", ""), "}"])
        call("java -javaagent:{}={} -cp {} {} {} {}".format(
            exp['instrumenter']['agent'],
            agent_options,
            classpath,
            exp['bootstrapper']['test-runner'],
            exp['d4j']['test-property'] + ".txt",
            "loaded.classes.txt"))

    return True

def checkout(project, version):
    path = project_path(project, version)

    call("mkdir -p {}".format(path))
    call("defects4j checkout -p {} -v {}b -w {}".format(project, version, path))

    os.chdir(path)

    call("defects4j compile")
    for prop in ["cp.test", exp['d4j']['test-property']]:
        call("defects4j export -p {0} -o {0}.txt".format(prop))

    loaded_classes = exp['d4j']['path'] + exp['d4j']['loaded-classes'].format(project, version)
    call("cp {} loaded.classes.txt".format(loaded_classes))

    return True

def validate_checkout(project, version):
    if project in exp['d4j']['projects']:
        try:
            rng = exp['d4j']['projects'][project]
            iversion = int(version)
            return iversion >= rng[0] and iversion <= rng[1]
        except:
            pass
    return False

if __name__ == "__main__":
    project = sys.argv[1]
    version = sys.argv[2]
    for f in [validate_checkout, checkout, run, export]:
        if not f(project, version):
            break
