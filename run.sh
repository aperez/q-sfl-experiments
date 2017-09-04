#!/usr/bin/env sh
set -e
project=$1
start=$2
max=$3

for (( i=$start; i<=$max; i++ ))
do
    echo "started $project $i" >> log.txt
    python3 scripts/main.py $project $i
    echo "finished $project $i" >> log.txt
done
