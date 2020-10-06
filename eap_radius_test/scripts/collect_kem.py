import shlex
import pprint
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pyshark
LOG_BASE_DIR = '../logs/'
LOG_DIR = f'{LOG_BASE_DIR}/kem'

def parse_algo(l):
    name = l.split('_')
    algo = ''
    if len(name) == 5:
        algo = name[4]
    else:
        algo = name[4] + '_' + name[5]
    return algo.split('.')[0]

def parse_bench(line, algo):
    line = line.rstrip()[7:]
    return dict(token.split('=') for token in shlex.split(line))

def parse_time(line, algo):
    s = line.rstrip().split(' ')
    return {'type': s[0], 'algo': algo,  'clock': s[1], 'cpu_time': s[2], 'wct': s[3]}

def parse_cap(packets):
    cap = []
    for x, packet in enumerate(packets):
        if 'radius' in packet:
            if 'avp' in packet.radius.field_names:
                print("True")
            print(packet.radius.field_names)
            print(packet.radius.eap_len)
            if 'eap_tls_len' in packet.radius.field_names:
                print(packet.radius.eap_tls_len)
        continue
        if packet.haslayer(scapy.all.Radius):
            for Radius in packet:
                for attribute in Radius.attributes:
                    d = {'algo': algo}
                    try:
                        if attribute.type is None:
                            attribute.show()
                    except Exception as e:
                        packet.show()
                        attribute.show()
                        print(e)
                        print(attribute)
                    d['type'] = int(attribute.type)
                    if attribute.len is None:
                        d['len'] = 0
                    else:
                        d['len'] = int(attribute.len)
                    cap.append(d)
    return cap


dirlist = os.listdir(LOG_DIR)
bench = []
time = []
cap = []
MIN=1
MAX=2
for i, l in enumerate(dirlist):
    if i < MIN or i > MAX:
        continue
    print(f'Parsing log {i}/{len(dirlist)}: {l}')
    algo = parse_algo(l)
    if l.endswith('_inst.log') or l.endswith('_time.log'):
        log = open(f'{LOG_DIR}/{l}','r')
        for line in log.readlines():
            if line.startswith('Bench: '):
                bench.append(parse_bench(line, algo))
            elif line.startswith('time_'):
                time.append(parse_time(line, algo))
            else:
                continue
    elif l.endswith('.cap'):
        packets = pyshark.FileCapture(f'{LOG_DIR}/{l}')
        cap += parse_cap(packets)
    else:
        print(f"Error unknown log {l}")
        sys.exit(1)
 
    log.close()

bench_df = pd.DataFrame(bench)
msg_cb = bench_df[bench_df['type'] == 'tls_msg_cb_bench'].copy()
info_cb = bench_df[bench_df['type'] == 'tls_info_cb_bench'].copy()
msg_cb['len'] = msg_cb['len'].astype('int64')
traffic = msg_cb.groupby(['rnd','groups']).sum().reset_index().sort_values('len')

time_df = pd.DataFrame(time)
time_df['clock'] = time_df['clock'].astype('float')
time_df['cpu_time'] = time_df['cpu_time'].astype('float')
time_df['wct'] = time_df['wct'].astype('float')
df_total = time_df[time_df['type'] == 'time_total']
df_eap = time_df[time_df['type'] == 'time_eap']

cap_df = pd.DataFrame(cap)
