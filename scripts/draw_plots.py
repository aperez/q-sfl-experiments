#!/usr/bin/env python3

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import scipy.stats
from math import sqrt
import operator

BASE_PATH = "data/"
PLOTS_PATH = "plots/"

DATA_INDEX = 2
DEFAULT_INDEX = 3
KNN_INDEX = 4
LINEAR_INDEX = 5
LOGISTIC_INDEX = 6
TREE_INDEX = 7
FOREST_INDEX = 8
XMEANS_INDEX = 9

DEFAULT_PARTITIONS_INDEX = 11
XMEANS_PARTITIONS_INDEX = 17

DELTA_PARTITIONS = DEFAULT_PARTITIONS_INDEX - DEFAULT_INDEX

def select_strategy(data):
    results = []
    for line in data:
        base = line[DATA_INDEX]
        best = None
        best_partitions = 0
        besti = 0
        for i in range(DEFAULT_PARTITIONS_INDEX,XMEANS_PARTITIONS_INDEX+1):
            current = line[i - DELTA_PARTITIONS]
            current_partitions = line[i]
            if current_partitions > 0:
                if not best or best > current:
                    best = current
                    best_partitions = current_partitions
                    besti = i
        results.append((base, best, besti - DELTA_PARTITIONS, line[0]))
    return results

def stats(filtered_strategy):
    a = [x[0] for x in filtered_strategy]
    b = [x[1] for x in filtered_strategy]
    ab = [x[0]-x[1] for x in filtered_strategy]
    print(scipy.stats.shapiro(a), np.mean(a), np.median(a), np.var(a))
    print(scipy.stats.shapiro(b), np.mean(b), np.median(b), np.var(b))
    print(scipy.stats.wilcoxon(ab))
    print(scipy.stats.norm.isf(5e-8 / 2))

def filter_partitions(data):
    return [x for x in data if sum(x[DEFAULT_PARTITIONS_INDEX:XMEANS_PARTITIONS_INDEX]) > 0]

def count_against_base(data, index=None):
    count = 0

    totals = [0,0,0]
    for line in data:
        counts = [0,0,0]
        for idx in range(DEFAULT_INDEX,XMEANS_INDEX+1):
            if index and idx != index:
                continue
            if line[DATA_INDEX] < line[idx]:
                counts[0] = 1
            elif line[DATA_INDEX] == line[idx]:
                counts[1] = 1
            else:
                counts[2] = 1
                break
        if counts[2] != 0:
            totals[2] += 1
        elif counts[1] != 0:
            totals[1] += 1
        else:
            totals[0] += 1
    return totals

def do_line_plot(data):
    mpl.rcParams['figure.figsize'] = (11, 6)
    ab = sorted([(x[0]-x[1], x[-1]) for x in data], key=operator.itemgetter(0))

    closure_ab = ([(x+1,y) for x,(y,z) in enumerate(ab) if z == "Closure"], "o", "0.12", "Closure")
    lang_ab = ([(x+1,y) for x,(y,z) in enumerate(ab) if z == "Lang"], "o", "0.55", "Commons Lang")
    math_ab = ([(x+1,y) for x,(y,z) in enumerate(ab) if z == "Math"], "o", "0.95", "Commons Math")
    chart_ab = ([(x+1,y) for x,(y,z) in enumerate(ab) if z == "Chart"], "^", "0.12", "JFreeChart")
    time_ab = ([(x+1,y) for x,(y,z) in enumerate(ab) if z == "Time"], "^", "0.55", "JodaTime")
    mockito_ab = ([(x+1,y) for x,(y,z) in enumerate(ab) if z == "Mockito"], "^", "0.95", "Mockito")

    fig, ax = plt.subplots()
    ax.set_axisbelow(True)
    plt.grid(True, color='0.75')

    for cat, marker, c, label in [closure_ab, lang_ab, math_ab, chart_ab, time_ab, mockito_ab]:
        plt.scatter([x[0] for x in cat], [x[1] for x in cat], c=c, lw=0.5,s=50, marker=marker, label=label, zorder=2)

    ax.set_yscale('symlog')
    ax.set_ylim([-200,1000])
    ax.set_xlim([0,len(ab)+2])
    plt.ylabel("$\Delta{}C_d$")
    plt.xlabel("Subject Number")
    plt.legend(scatterpoints=1,
               loc='lower right',
               fontsize="10")
    ax.axvline(15.5, lw=0.25, color='red',ls='--', zorder=1)
    ax.axvline(77.5, lw=0.25, color='green',ls='--', zorder=1)
    ax.axvspan(0, 15.5, alpha=0.11, color='red', zorder=0)
    ax.axvspan(77.5, len(ab)+2, alpha=0.11, color='green', zorder=0)

    ax.annotate('$\Delta{}C_d \geq 0$', xy=(15.25, 300),  xycoords='data',
                xytext=(18, -3), textcoords='offset points',
                arrowprops=dict(arrowstyle="<-"), size=10,
                bbox=dict(boxstyle="square", pad=0, alpha=0)
                )

    ax.annotate('$\Delta{}C_d < 0$', xy=(15.5, 500),  xycoords='data',
                xytext=(-55, -3), textcoords='offset points',
                arrowprops=dict(arrowstyle="<-"), size=10,
                bbox=dict(boxstyle="square", pad=0, alpha=0)
                )

    ax.annotate('$\Delta{}C_d > 0$', xy=(77.25, 300),  xycoords='data',
                xytext=(18, -3), textcoords='offset points',
                arrowprops=dict(arrowstyle="<-"), size=10,
                bbox=dict(boxstyle="square", pad=0, alpha=0)
                )

    ax.annotate('$\Delta{}C_d \leq 0$', xy=(77.5, 500),  xycoords='data',
                xytext=(-55, -3), textcoords='offset points',
                arrowprops=dict(arrowstyle="<-"), size=10,
                bbox=dict(boxstyle="square", pad=0, alpha=0)
                )

    plt.tight_layout()
    plt.savefig(PLOTS_PATH + "delta-cd.pdf", bbox_inches="tight")

def do_plot(results, my_xticks, filename, xlabel='', ylabel='', title=''):
    # data to plot
    n_groups = len(results)
    #results = count_against_base(data)
    results_better = [x[0] for x in results]
    results_same = [x[1] for x in results]
    results_worse = [x[2] for x in results]

    # create plot
    fig, ax = plt.subplots()
    ax.set_axisbelow(True)
    plt.grid(True, color='0.75')

    index = np.arange(n_groups)
    bar_width = 0.275
    opacity = 0.8

    rects1 = plt.bar(index, results_better, bar_width,
                     color='0.45',  lw=1.2,
                     label='$\Delta{}C_d$ < 0')

    rects2 = plt.bar(index + bar_width, results_same, bar_width,
                     hatch='////', lw=1.2,
                     color='0.65',
                     label='$\Delta{}C_d$ = 0')

    rects3 = plt.bar(index + bar_width + bar_width, results_worse, bar_width,
                     hatch='xxxx', lw=1.2,
                     color='0.95',
                     edgecolor='black',
                     label='$\Delta{}C_d$ > 0')

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(index + 1.5*bar_width, my_xticks)
    plt.legend(fontsize="12")
    plt.tight_layout()
    plt.savefig(PLOTS_PATH + filename, bbox_inches="tight")

if __name__ == "__main__":
    data = []
    for f in ["Closure.csv", "Lang.csv", "Math.csv", "Chart.csv","Time.csv","Mockito.csv"]:
        with open(BASE_PATH + f) as projectfile:
            for index, line in enumerate(projectfile):
                if index==0:
                    continue
                line = line.rstrip().split(",")
                for x in range(2,len(line)):
                    line[x] = float(line[x])
                data.append(line)

    data = filter_partitions(data)
    fstrat = select_strategy(data)
    #stats(fstrat)

    results = [count_against_base(data, DEFAULT_INDEX),
               count_against_base(data, XMEANS_INDEX),
               count_against_base(data, KNN_INDEX),
               count_against_base(data, LINEAR_INDEX),
               count_against_base(data, LOGISTIC_INDEX),
               count_against_base(data, TREE_INDEX),
               count_against_base(data, FOREST_INDEX)
               ]

    do_plot(results, ['Default','X-means', 'k-NN','Linear', 'Logistic', 'Tree', 'Forest'],
            'per-strategy.pdf', xlabel='Strategies',ylabel='# Subjects',
            title='Effort vs Base: All Projects')

    do_line_plot(fstrat)
