import shlex
import pprint
import pandas as pd
log = open('a.out', 'r')
res = []
for line in log.readlines():
    if not line.startswith('Bench: '):
        continue
    line = line.rstrip()[7:]
    res.append(dict(token.split('=') for token in shlex.split(line)))

df = pd.DataFrame(res)

    