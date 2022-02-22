import sqlite3
import sys
import ipdb
import numpy as np
import seaborn as sns
import ast
import matplotlib.pyplot as plt
from collections import defaultdict

def getKeyWord(url):
    url = url.split("://")[1]
    url = url.split(".")
    if url[0] == 'www':
        return url[1]
    return url[0]

def main():
    url2group, url2idx = {}, {}
    groups = set()
    with open('urlsWcategory.csv') as file:
        for row in file:
            row = row.split(",")
            if row[0][-1] != '/':
                row[0] += '/'
            urlKeyWord = getKeyWord(row[0])
            url2group[urlKeyWord] = row[1].strip()
            groups.add(row[1].strip())

    covariance = [[0 for _ in range(len(groups))] for _ in range(len(groups))]
    group2idx = {x:i for i, x in enumerate(groups)}
    print(group2idx)
    con = sqlite3.connect('exp/with_category/crawl-data.sqlite')
    cur = con.cursor()
    stats = defaultdict(set)
    # Insert a row of data
    rows = cur.execute("SELECT t.loading_origin, t.headers FROM http_requests AS t WHERE t.referrer != ''").fetchall()
    headerCount = 0
    for row in rows:
        header = ast.literal_eval(row[1])
        # ipdb.set_trace()
        stats[header[0][1]].add(getKeyWord(row[0]))
        if header[1][0] == 'User-Agent':
            headerCount += 1
    ipdb.set_trace()
    
    con.close()
    for key in stats:
        stats[key] = list(stats[key])
        for i in range(len(stats[key])):
            for j in range(1, len(stats[key])):
                try:
                    i_idx = group2idx[url2group[stats[key][i]]]
                    j_idx = group2idx[url2group[stats[key][j]]]
                    covariance[i_idx][j_idx] += 1
                    covariance[j_idx][i_idx] += 1
                except:
                    pass

    ax = sns.heatmap(covariance, linewidth=0.5)
    ax.set_xlabel('Group Number')
    ax.set_ylabel('Group Number')
    plt.savefig('heatmap.png', bbox_inches="tight")

    plt.rcdefaults()
    fig, ax = plt.subplots()

    # Example data
    stats = [(key, stats[key]) for key in stats]
    stats = sorted(stats, key=lambda x: -len(x[1]))[:20]
    people = [x[0] for x in stats]
    y_pos = np.arange(len(people))
    performance = [len(x[1]) for x in stats]

    ax.barh(y_pos, performance, align='center')
    ax.set_yticks(y_pos, labels=people)
    ax.invert_yaxis()  # labels read top-to-bottom
    ax.set_xlabel('Frequency')
    ax.set_title('Trackers')

    plt.savefig('tracker_freq.png', bbox_inches="tight")

if __name__ == '__main__':
    with ipdb.launch_ipdb_on_exception():
        sys.breakpointhook = ipdb.set_trace
        main()
