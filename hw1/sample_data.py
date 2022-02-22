from collections import defaultdict
from random import sample

dataset = defaultdict(list)
ds_o = []
with open('../archive/URL_Classification.csv') as file:
    for row in file:
        row = row.strip().split(',')[1:]
        dataset[row[1]].append(row[0])
for k in dataset:
    urls = sample(dataset[k], 6)
    ds_o.append([urls, k])
with open('urlsWcategory.csv', 'w') as file:
    for (urls, category) in ds_o:
        for url in urls:
            file.write(','.join([url, category])+'\n')