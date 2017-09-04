#!/usr/bin/env python3

import subprocess
from valueprobes_parser import *

FL_BASE_PATH="fault-localization-data/analysis/pipeline-scripts/buggy-lines"

CP = "q-sfl/instrumenter/target/qsfl-instrumenter-0.1-SNAPSHOT-with-dependencies.jar:"+\
     "q-sfl/bootstrapper/target/qsfl-bootstrapper-0.1-SNAPSHOT.jar"

COMMAND = "pt.up.fe.qsfl.bootstrapper.FaultLocation"

def call(command, timeout=None):
    print(command)
    return subprocess.call(command.split(' '),timeout=timeout)

def run_fault_locator(project, version):
    path = project_path(project, version)
    print(path)

    buggy_lines = "{}/{}-{}.buggy.lines".format(FL_BASE_PATH, project, version)
    call("java -cp {} {} {} {}".format(CP, COMMAND, path, buggy_lines))

if __name__ == "__main__":
    project = sys.argv[1]
    version = sys.argv[2]
    run_fault_locator(project, version)
