import shlex
import pprint
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import subprocess
import json
import pprint
LOG_BASE_DIR = '../logs/'
LOG_DIR = f'{LOG_BASE_DIR}/kem'

def parse_algo(l):
    name = l.split('_')
    algo = ''
    ts = name[1]
    run = name[-2]
    if len(name) == 5:
        algo = name[4]
    else:
        algo = name[4] + '_' + name[5]
    return (algo.split('.')[0], ts, run)

def parse_bench(line, algo, ts, run):
    line = line.rstrip()[7:]
    d = dict(token.split('=') for token in shlex.split(line))
    d['ts'] = ts
    d['run'] = run
    return d

def parse_time(line, algo, ts, run):
    s = line.rstrip().split(' ')
    return {'run': run, 'ts': ts, 'type': s[0], 'algo': algo,  'clock': s[1], 'cpu_time': s[2], 'wct': s[3]}

def parse_cap(packets, algo, ts, run):
    cap = []
    for x, packet in enumerate(packets):
        d  ={'algo': algo, 'ts': ts, 'run': run}
        #d['index'] = packet['_index']
        packet = packet['_source']
        d['time'] = packet['layers']['frame']['frame.time']
        d['time_delta'] = packet['layers']['frame']['frame.time_delta']
        d['frame_nr'] = packet['layers']['frame']['frame.number']
        d['frame_len'] = packet['layers']['frame']['frame.len']
        d['src'] = packet['layers']['udp']['udp.srcport']
        d['dst'] = packet['layers']['udp']['udp.dstport']
        radius = packet['layers']['radius']
        d['rad_len'] = radius['radius.length']
        d['rad_code'] = radius['radius.code']
        d['rad_id'] = radius['radius.id']
        avp = radius['Attribute Value Pairs']['radius.avp_tree']
        for x in avp:
            for k in x:
                if k == 'radius.avp.type':
                    d['rad_avp_t'] = x['radius.avp.type']
                elif k == 'radius.avp.length':
                    d['rad_avp_len'] = x['radius.avp.length']
                else:
                    pass
                    #d['rad_avp_payload'] = x[k]
        cap.append(d)
    return cap

dirlist = os.listdir(LOG_DIR)
bench = []
time = []
cap = []
MIN=0
MAX=len(dirlist)
for i, l in enumerate(dirlist):
    if i < MIN or i > MAX:
        continue
    print(f'Parsing log {i}/{len(dirlist)}: {l}')
    algo, ts, run = parse_algo(l)
    if l.endswith('_inst.log') or l.endswith('_time.log'):
        log = open(f'{LOG_DIR}/{l}','r')
        for line in log.readlines():
            if line.startswith('Bench: '):
                bench.append(parse_bench(line, algo, ts, run))
            elif line.startswith('time_'):
                time.append(parse_time(line, algo, ts, run))
            else:
                continue
    elif l.endswith('.cap'):
        continue
        capfile = f'{LOG_DIR}/{l}'
        tshark = ('tshark', '-2', '-r', capfile, '-T', 'json', '--no-duplicate-keys')
        o = subprocess.Popen(tshark, stdout=subprocess.PIPE)
        out = o.communicate()[0]
        out = json.loads(out)
        cap += parse_cap(out, algo, ts, run)
    else:
        print(f"Error unknown log {l}")
        sys.exit(1)
    log.close()

bench_df = pd.DataFrame(bench)
msg_cb = bench_df[bench_df['type'] == 'tls_msg_cb_bench'].copy().dropna(axis='columns')
info_cb = bench_df[bench_df['type'] == 'tls_info_cb_bench'].copy().dropna(axis='columns')
msg_cb['len'] = msg_cb['len'].astype('int64')
traffic = msg_cb.groupby(['rnd','groups']).sum().reset_index().sort_values('len')
msg_cb['clock'] = msg_cb['clock'].astype(np.uint64)
msg_cb['clock_delta'] = msg_cb['clock_delta'].astype(np.uint64)
msg_cb['clock_abs'] = msg_cb['clock_abs'].astype(np.uint64)
msg_cb['time'] = msg_cb['time'].astype(np.uint64)
msg_cb['time_delta'] = msg_cb['time_delta'].astype(np.uint64)
msg_cb['time_abs'] = msg_cb['time_abs'].astype(np.uint64)
info_cb['clock'] = info_cb['clock'].astype(np.uint64)
info_cb['clock_delta'] = info_cb['clock_delta'].astype(np.uint64)
info_cb['clock_abs'] = info_cb['clock_abs'].astype(np.uint64)
info_cb['time'] = info_cb['clock_delta'].astype(np.uint64)
info_cb['time_delta'] = info_cb['time_delta'].astype(np.uint64)
info_cb['time_abs'] = info_cb['time_abs'].astype(np.uint64)

info_cb['n'] = info_cb['n'].astype(np.uint64)

msg_cb['sum_len'] = msg_cb['sum_len'].astype(np.uint64)
msg_cb['n'] = msg_cb['n'].astype(np.uint64)

time_df = pd.DataFrame(time)
time_df['clock'] = time_df['clock'].astype('float')
time_df['cpu_time'] = time_df['cpu_time'].astype('float')
time_df['wct'] = time_df['wct'].astype('float')
df_total = time_df[time_df['type'] == 'time_total']
df_eap = time_df[time_df['type'] == 'time_eap']

cap_df = pd.DataFrame(cap)
