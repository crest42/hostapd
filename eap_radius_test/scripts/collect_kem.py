import shlex
import pprint
import pandas as pd
import os

LOG_BASE_DIR = '../logs/'
LOG_DIR = f'{LOG_BASE_DIR}/kem'

dirlist = os.listdir(LOG_DIR)
res = []
for i, l in enumerate(dirlist):
    print(f'Parsing log {i}/{len(dirlist)}')
    log = open(f'{LOG_DIR}/{l}','r')
    for line in log.readlines():
        if not line.startswith('Bench: '):
            continue
        line = line.rstrip()[7:]
        res.append(dict(token.split('=') for token in shlex.split(line)))
    log.close()

df = pd.DataFrame(res)
df['len'] = df['len'].astype('int64')
df['cycles'] = df['clocks'].astype('int64')
msg_cb = df[df['type'] == 'tls_msg_cb_bench']
info_cb = df[df['type'] == 'tls_info_cb_bench']

traffic = msg_cb.groupby(['rnd','groups']).sum().reset_index().sort_values('len')
cycles = info_cb.groupby(['rnd','groups']).sum().reset_index().sort_values('clocks')
