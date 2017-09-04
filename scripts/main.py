import os
import sys
import imp
import time
import subprocess

load = lambda f: imp.load_source(f, 'scripts/{}.py'.format(f))

run_default_landmarks = load('run_default_landmarks')
run_classification_landmarks = load('run_classification_landmarks')
run_fault_locator = load('run_fault_locator')
run_diagnosis_native = load('run_diagnosis_native')

BASE_PATH="data"

def project_path(project, version, base=BASE_PATH):
    return "{}/{}/{}".format(base, project, version)

def call(command, timeout=None):
    print(command)
    return subprocess.call(command.split(' '),timeout=timeout)

def run(project, version):
    path = project_path(project, version)
    pwd = os.getcwd()
    image = "qsfljdk8" if project == "Mockito" else "qsfl"
    start = time.time()
    #run docker command
    cmd = "docker run -it -v {}/data:/data {} python3 run_experiment.py {} {}"\
            .format(pwd, image, project, version)
    call(cmd)

    #check if directory was created
    if os.path.isdir(path):
        run_default_landmarks.create_thresholds(project, version)
        run_classification_landmarks.create_thresholds(project, version)
        run_fault_locator.run_fault_locator(project, version)
        run_diagnosis_native.run_diagnosis(project, version)

        elapsed = time.time() - start
        print(project, version, "elapsed time:", elapsed)

        with open(path+"/time.seconds", "w") as t:
            t.write(str(elapsed))

if __name__ == "__main__":
    project = sys.argv[1]
    version = sys.argv[2]
    run(project, version)
