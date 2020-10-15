import shlex
import pprint
import pandas as pd
import os
import seaborn
import sys
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

def _parse(min=0, max=None):
    bench = []
    time = []
    cap = []
    dirlist = os.listdir(LOG_DIR)
    if max is None:
        max=len(dirlist)
    for i, l in enumerate(dirlist):
        if i < min or i > max:
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
    msg_cb['len'] = msg_cb['len'].astype('int64')
    msg_cb['clock'] = msg_cb['clock'].astype(float)
    msg_cb['clock_delta'] = msg_cb['clock_delta'].astype(float)
    msg_cb['clock_abs'] = msg_cb['clock_abs'].astype(float)
    msg_cb['time'] = msg_cb['time'].astype(float)
    msg_cb['time_delta'] = msg_cb['time_delta'].astype(float)
    msg_cb['time_abs'] = msg_cb['time_abs'].astype(float)
    msg_cb['sum_len'] = msg_cb['sum_len'].astype(float)
    msg_cb['n'] = msg_cb['n'].astype(int)

    info_cb = bench_df[bench_df['type'] == 'tls_info_cb_bench'].copy().dropna(axis='columns')
    info_cb['clock'] = info_cb['clock'].astype(float)
    info_cb['clock_delta'] = info_cb['clock_delta'].astype(float)
    info_cb['clock_abs'] = info_cb['clock_abs'].astype(float)
    info_cb['time'] = info_cb['clock_delta'].astype(float)
    info_cb['time_delta'] = info_cb['time_delta'].astype(float)
    info_cb['time_abs'] = info_cb['time_abs'].astype(float)
    info_cb['n'] = info_cb['n'].astype(float)

    time_df = pd.DataFrame(time)
    time_df['clock'] = time_df['clock'].astype('float')
    time_df['cpu_time'] = time_df['cpu_time'].astype('float')
    time_df['wct'] = time_df['wct'].astype('float')
    df_total = time_df[time_df['type'] == 'time_total']
    df_eap = time_df[time_df['type'] == 'time_eap']

    cap_df = pd.DataFrame(cap)
    return msg_cb.reset_index().drop(['index', 'type'], axis=1), info_cb.reset_index().drop(['index','type'],axis=1), df_total, df_eap, cap_df


def main(load=None, store=None):
    if load is not None:
        msg_cb = pd.read_pickle("./pkl/msg_cb.pkl")
        info_cb = pd.read_pickle("./pkl/info_cb.pkl")
        df_total = pd.read_pickle("./pkl/df_total.pkl")
        df_eap = pd.read_pickle("./pkl/df_eap.pkl")
        cap_df = pd.read_pickle("./pkl/cap_df.pkl")
        return (msg_cb, info_cb, df_total, df_eap, cap_df)
    else:
        (msg_cb, info_cb, df_total, df_eap, cap_df) = _parse()
    if store is not None:
        msg_cb.to_pickle("./pkl/msg_cb.pkl")
        info_cb.to_pickle("./pkl/info_cb.pkl")
        df_total.to_pickle("./pkl/df_total.pkl")
        df_eap.to_pickle("./pkl/df_eap.pkl")
        cap_df.to_pickle("./pkl/cap_df.pkl")
    
    return (msg_cb, info_cb, df_total, df_eap, cap_df)


(msg_cb, info_cb, df_total, df_eap, cap_df) = None, None, None, None, None

if __name__ == '__main__':
    load = None
    store = None
    if len(sys.argv) > 1:
        if sys.argv[1] == 'load':
            load = True
        if sys.argv[1] == 'store':
            store = True
    (msg_cb, info_cb, df_total, df_eap, cap_df) = main(load=load, store=store)
else:
    (msg_cb, info_cb, df_total, df_eap, cap_df) = main('load')


PQ_L1_CURVES = ["bike1l1cpa", "bike1l1fo",
               "frodo640aes", "frodo640shake",
               "hqc128_1_cca2",
               "kyber512", "kyber90s512",
               "ntru_hps2048509",
               "lightsaber",
               "sidhp434", "sidhp503", "sikep434", "sikep503", 'P-256']

PQ_L3_CURVES = ["bike1l3cpa", "bike1l3fo",
               "frodo976aes", "frodo976shake",
               "hqc192_1_cca2", "hqc192_2_cca2",
               "kyber768", "kyber90s768",
               "ntru_hps2048677", "ntru_hrss701",
               "saber",
               "sidhp610", "sikep610", 'P-384']


PQ_L5_CURVES = ["frodo1344aes", "frodo1344shake",
                "hqc256_1_cca2", "hqc256_2_cca2", "hqc256_3_cca2",
                "kyber1024", "kyber90s1024",
                "ntru_hps4096821",
                "firesaber",
                "sidhp751", "sikep751", 'P-521']

def add_sec_level(df, x):
    df['hybrid'] = np.where(df[x].str.startswith('p256_') | df[x].str.startswith('p384_') | df[x].str.startswith('p521_'), True, False)
    df['classical_algo'] = [xv[0] if c else None for c, xv, yv in zip(df['hybrid'] == True, df[x].str.split('_'), df[x])]
    df['pq_algo'] = ['_'.join(xv[1:]) if c else yv for c, xv, yv in zip(df['hybrid'] == True, df[x].str.split('_'), df[x])]
    df['sec_level'] = [1 if a in PQ_L1_CURVES else 3 if a in PQ_L3_CURVES else 5 for a in df['pq_algo']]
    return df

df_total = add_sec_level(df_total, 'algo')
df_eap = add_sec_level(df_eap, 'algo')
msg_cb = add_sec_level(msg_cb, 'groups')
msg_cb['rutime'] = msg_cb['rutime'].astype(float)
msg_cb['rstime'] = msg_cb['rstime'].astype(float)

