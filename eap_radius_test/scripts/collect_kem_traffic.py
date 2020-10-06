import shlex
import pprint
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

LOG_BASE_DIR = '../logs/'
LOG_DIR = f'{LOG_BASE_DIR}/kem'

dirlist = os.listdir(LOG_DIR)
res = []
for i, l in enumerate(dirlist):
    print(f'Parsing log {i}/{len(dirlist)}')
    log = open(f'{LOG_DIR}/{l}','r')
    name = l.split('_')
    algo = ''
    if len(name) == 5:
        algo = name[4]
    else:
        algo = name[4] + '_' + name[5]
    algo = algo.split('.')[0]
    for line in log.readlines():
        if not line.startswith('time_'):
            continue
        s = line.rstrip().split(' ')
        res.append({'type': s[0], 'algo': algo,  'clock': s[1], 'cpu_time': s[2], 'wct': s[3]})
    log.close()


df = pd.DataFrame(res)
df['clock'] = df['clock'].astype('float')
df['cpu_time'] = df['cpu_time'].astype('float')
df['wct'] = df['wct'].astype('float')
df_total = df[df['type'] == 'time_total']
df_eap = df[df['type'] == 'time_eap']

result = df_total.groupby(["algo"])['clock'].aggregate(np.mean).reset_index().sort_values('clock')