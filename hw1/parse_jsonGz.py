import json
from bs4 import BeautifulSoup
import gzip
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

fingerprintScripts = {}
weights = {}
with open('fingerprintScripts.txt', 'r') as file:
    count = 0
    for row in file:
        scriptName, weight = row.strip().split(',')
        weights[scriptName] = float(weight)
        fingerprintScripts[scriptName] = 0
        count += 1
        if count > 500:
            break

pathlists = [Path('exp/with_category/sources/').glob('**/*.gz')]
for pathlist in pathlists:
    for path in pathlist:
        # because path is object not string
        filename = str(path)

        with gzip.open(filename , 'rb') as gzip_file:
            data = gzip_file.read()
            obj = json.loads(data.decode('utf-8'))

        soup = BeautifulSoup(obj['source'], 'html.parser')
        for script in soup.find_all('script'):
            script = str(script)
            for fingerprintScript in fingerprintScripts:
                try: 
                    scriptIdx = script.index(fingerprintScript)
                    if (scriptIdx == 0 or not script[scriptIdx-1].isalpha()) and (scriptIdx == len(script)-1 or not script[scriptIdx+len(fingerprintScript)].isalpha()):
                        fingerprintScripts[fingerprintScript] += 1
                        # import ipdb; ipdb.set_trace()
                except:
                    pass
                    

plt.rcdefaults()
fig, ax = plt.subplots()
# Example data
stats = [(key, fingerprintScripts[key]) for key in fingerprintScripts if fingerprintScripts[key] > 0]
stats = sorted(stats, key=lambda x: -x[1])[:30]
people = [x[0] for x in stats]
y_pos = np.arange(len(people))
performance = [x[1] for x in stats]

ax.barh(y_pos, performance, align='center')
ax.set_yticks(y_pos, labels=people)
ax.invert_yaxis()  # labels read top-to-bottom
ax.set_xlabel('Raw Frequency')
ax.set_title('Top 30 FingerprintScripts')

plt.show()
plt.savefig('Fingerprint.png', bbox_inches="tight")