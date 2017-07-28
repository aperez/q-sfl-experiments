#!/usr/bin/env python3

import subprocess
from valueprobes_parser import *

CP = "data-sfl/instrumenter/target/ddsfl-instrumenter-0.1-SNAPSHOT-with-dependencies.jar:"+\
     "data-sfl/diagnoser/target/ddsfl-diagnoser-0.1-SNAPSHOT.jar:"+\
     "data-sfl/bootstrapper/target/ddsfl-bootstrapper-0.1-SNAPSHOT.jar"

COMMAND = "pt.up.fe.ddsfl.bootstrapper.Diagnosis"

CRITERIA = ['default',
            'knn',
            'tree',
            'forest',
            'linear',
            'logistic',
            'xmeans']

def call(command, timeout=None):
    print(command)
    return subprocess.call(command.split(' '),timeout=timeout)

def run_fault_locator(project, version):
    path = project_path(project, version)
    print(path)

    call("java -cp {} {} {}".format(CP, COMMAND, path))
    for criterion in CRITERIA:
        call("java -cp {} {} {} {}".format(CP, COMMAND, path, criterion))

if __name__ == "__main__":
    project = sys.argv[1]
    version = sys.argv[2]
    run_fault_locator(project, version)
