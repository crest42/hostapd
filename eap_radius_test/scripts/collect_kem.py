import shlex
import os
import sys
import subprocess
import json
import pprint
import numpy as np
import pandas as pd
APPEND = '_0ms'
LOG_BASE_DIR = '../logs/'
LOG_DIR = f'{LOG_BASE_DIR}/kem{APPEND}'

def parse_algo(l):
    split = l.split('_')
    ts = split[1]
    run = split[-2]
    algo = '_'.join(split[4:-2]).split('.')[0]
    return (algo, ts, run)

def parse_bench(line, algo, ts, run):
    line = line.rstrip()[7:]
    d = dict(token.split('=') for token in shlex.split(line))
    d['algo'] = algo
    d['ts'] = ts
    d['run'] = run
    return d

def parse_time(line, algo, ts, run):
    s = line.rstrip().split(' ')
    return {'run': run, 'ts': ts, 'type': s[0], 'algo': algo,  'clock': s[1], 'cpu_time': s[2], 'wct': s[3]}

def __get_frame_info(frame, d):
    d['time'] = frame['frame.time']
    d['time_delta'] = frame['frame.time_delta']
    d['frame_nr'] = frame['frame.number']
    d['frame_len'] = frame['frame.len']
    return d

def __get_udp_info(udp, d):
    d['src'] = udp['udp.srcport']
    d['dst'] = udp['udp.dstport']
    return d

def __get_rad_info(radius, d):
    d['rad_len'] = radius['radius.length']
    d['rad_code'] = radius['radius.code']
    d['rad_id'] = radius['radius.id']
    return d

def __parse_tls_real_type(__d):
    if 'tls.handshake.type' in __d:
        __d['tls_real_type'] = __d['tls.handshake.type']
    elif 'tls.record.opaque_type' in __d:
        __d['tls_real_type'] = __d['tls.record.opaque_type']
    else:
        __d['tls_real_type'] = __d['tls.record.content_type']
    return __d

def __parse_tls_record_fields(record, __d):
    for field in record:
        if field == 'tls.record.version':
            __d['tls.record.version'] = record['tls.record.version']
        elif field == 'tls.record.opaque_type':
            __d['tls.record.content_type'] = record['tls.record.opaque_type']
        elif field == 'tls.record.content_type':
            __d['tls.record.content_type'] = record['tls.record.content_type']
        elif field == 'tls.record.length':
            __d['tls.record.length'] =  record['tls.record.length']
        elif field == 'tls.handshake':
            if 'tls.handshake.type' in record[field]:
                __d['tls.handshake.type'] = record[field]['tls.handshake.type']
            if 'tls.handshake.length' in record[field]:
                __d['tls.handshake.length'] = record[field]['tls.handshake.length']
        else:
            pass
    return __parse_tls_real_type(__d)

def __parse_eap(eap, _d):
    _d['eap.id'] = eap['eap.id']
    _d['eap.code'] = eap['eap.code']
    _d['eap.len'] = eap['eap.len']
    if 'eap.type' in eap:
        _d['eap.type'] = eap['eap.type']
    return _d


def parse_cap(capfile, algo, ts, run):
    cap = []
    tshark = ('tshark', '-n', '-2', '-r', capfile, '-T', 'json', '--no-duplicate-keys')
    o = subprocess.Popen(tshark, stdout=subprocess.PIPE)
    packets = json.loads(o.communicate()[0])
    pkt_count = 0
    for _x, packet in enumerate(packets):
        d = {'algo': algo, 'ts': ts, 'run': run}
        packet = packet['_source']
        d = __get_frame_info(packet['layers']['frame'], d)
        if 'radius' not in packet['layers']:
            continue
        d['frame_count'] = pkt_count
        pkt_count += 1
        d = __get_udp_info(packet['layers']['udp'], d)
        d = __get_rad_info(packet['layers']['radius'], d)
        radius = packet['layers']['radius']
        for avp_count, x in enumerate(radius['Attribute Value Pairs']['radius.avp_tree']):
            has_tls_layer = False
            _d = d.copy()
            _d['avp_count'] = avp_count
            for k in x:
                if k == 'radius.avp.type':
                    _d['rad_avp_t'] = x['radius.avp.type']
                elif k == 'radius.avp.length':
                    _d['rad_avp_len'] = x['radius.avp.length']
                elif k == 'eap':
                    if _x == 0:
                        assert(x[k]['eap.code'] == '2' and x[k]['eap.type'] == '1')
                    if _x == len(packets)-1:
                        assert(x[k]['eap.code'] == '3')
                    _d = __parse_eap(x[k], _d)
                    if 'tls' in x[k]:
                        if not isinstance(x[k]['tls'],str):
                            for _k in x[k]['tls']:
                                if _k == 'tls.record':
                                    records = x[k]['tls'][_k]
                                    if isinstance(records, dict):
                                        records = [records]
                                    if len(records) > 0:
                                        has_tls_layer = True
                                    for i, record in enumerate(records):
                                        __d = __parse_tls_record_fields(record, _d.copy())
                                        __d['record_count'] = i
                                        cap.append(__d)
                                elif _k == 'Ignored Unknown Record':
                                    pass
                                else:
                                    print(d['frame_nr'])
                                    pprint.pprint(x[k])
            if not has_tls_layer:
                cap.append(_d)
    return cap

def parse_inst(instfile, algo, ts, run):
    log = open(instfile,'r')
    bench = []
    time = []
    for line in log.readlines():
        if line.startswith('Bench: '):
            bench.append(parse_bench(line, algo, ts, run))
        elif line.startswith('time_'):
            time.append(parse_time(line, algo, ts, run))
        else:
            continue
    log.close()
    return bench, time

def beautify_msg(_msg_cb):
    _msg_cb['len'] = _msg_cb['len'].astype('int64')
    _msg_cb['clock'] = _msg_cb['clock'].astype(float)
    _msg_cb['clock_delta'] = _msg_cb['clock_delta'].astype(float)
    _msg_cb['clock_abs'] = _msg_cb['clock_abs'].astype(float)
    _msg_cb['time'] = _msg_cb['time'].astype(float)
    _msg_cb['time_delta'] = _msg_cb['time_delta'].astype(float)
    _msg_cb['time_abs'] = _msg_cb['time_abs'].astype(float)
    _msg_cb['sum_len'] = _msg_cb['sum_len'].astype(float)
    _msg_cb['n'] = _msg_cb['n'].astype(int)
    _msg_cb = _msg_cb.reset_index().drop(['index', 'type'], axis = 1)
    return _msg_cb

def beautify_info(_info_cb):
    _info_cb['clock'] = _info_cb['clock'].astype(float)
    _info_cb['clock_delta'] = _info_cb['clock_delta'].astype(float)
    _info_cb['clock_abs'] = _info_cb['clock_abs'].astype(float)
    _info_cb['time'] = _info_cb['clock_delta'].astype(float)
    _info_cb['time_delta'] = _info_cb['time_delta'].astype(float)
    _info_cb['time_abs'] = _info_cb['time_abs'].astype(float)
    _info_cb['n'] = _info_cb['n'].astype(float)
    _info_cb = _info_cb.reset_index().drop(['index', 'type'], axis = 1)
    return _info_cb

def beautify_time(_time_df):
    _time_df['clock'] = _time_df['clock'].astype('float')
    _time_df['cpu_time'] = _time_df['cpu_time'].astype('float')
    _time_df['wct'] = _time_df['wct'].astype('float')
    _df_total = _time_df[_time_df['type'] == 'time_total']
    _df_eap = _time_df[_time_df['type'] == 'time_eap']
    return _df_total, _df_eap

def beautify_cap(_cap_df):
    _cap_df['frame_nr'] = _cap_df['frame_nr'].astype(int)
    _cap_df['ts'] = _cap_df['ts'].astype(int)
    _cap_df['run'] = _cap_df['run'].astype(int)
    _cap_df['time'] = pd.to_datetime(_cap_df['time'])
    _cap_df['time_delta'] = _cap_df['time_delta'].astype(float)
    _cap_df['frame_len'] = _cap_df['frame_len'].astype(int)
    _cap_df['rad_len'] = _cap_df['rad_len'].astype(int)
    _cap_df['rad_avp_len'] = _cap_df['rad_avp_len'].astype(int)
    _cap_df['eap.len'] = _cap_df['eap.len'].astype(float)
    _cap_df['tls.record.length'] = _cap_df['tls.record.length'].astype(float)
    _cap_df['tls.handshake.length'] = _cap_df['tls.handshake.length'].astype(float)
    return _cap_df

def beautify(bench, time, cap):
    _msg_cb = None
    _info_cb = None
    _df_total = None
    _df_eap = None
    _cap_df = None

    bench_df = pd.DataFrame(bench)
    if len(bench_df) > 0:
        _msg_cb = bench_df[bench_df['type'] == 'tls_msg_cb_bench'].copy().dropna(axis='columns')
        _msg_cb = beautify_msg(_msg_cb)

    if len(bench_df) > 0:
        _info_cb = bench_df[bench_df['type'] == 'tls_info_cb_bench'].copy().dropna(axis='columns')
        _info_cb = beautify_info(_info_cb)

    time_df = pd.DataFrame(time)
    if len(time_df) > 0:
        _df_total, _df_eap = beautify_time(time_df)

    _cap_df = pd.DataFrame(cap)
    if len(_cap_df) > 0:
        _cap_df = beautify_cap(_cap_df)

    return _msg_cb, _info_cb, _df_total, _df_eap, _cap_df

def _parse(_min=0, _max=None):
    bench = []
    time = []
    cap = []
    dirlist = os.listdir(LOG_DIR)
    if _max is None:
        _max=len(dirlist)
    for i, l in enumerate(dirlist):
        if i < _min or i > _max:
            continue
        print(f'Parsing log {i}/{len(dirlist)}: {l}')
        algo, ts, run = parse_algo(l)
        if l.endswith('_inst.log'):
            instfile = f'{LOG_DIR}/{l}'
            a = []
            b = []
            a, b = parse_inst(instfile, algo, ts, run)
            bench += a
            time += b
        elif l.endswith('.cap'):
            capfile = f'{LOG_DIR}/{l}'
            cap += parse_cap(capfile, algo, ts, run)
        else:
            print(f"Error unknown log {l}")
            sys.exit(1)

    return beautify(bench, time, cap)


def main(load=None, store=None):
    if load is not None:
        _msg_cb = pd.read_pickle(f"./pkl/msg_cb{APPEND}.pkl")
        _info_cb = pd.read_pickle(f"./pkl/info_cb{APPEND}.pkl")
        _df_total = pd.read_pickle(f"./pkl/df_total{APPEND}.pkl")
        _df_eap = pd.read_pickle(f"./pkl/df_eap{APPEND}.pkl")
        _cap_df = pd.read_pickle(f"./pkl/cap_df{APPEND}.pkl")
        return (_msg_cb, _info_cb, _df_total, _df_eap, _cap_df)
    (_msg_cb, _info_cb, _df_total, _df_eap, _cap_df) = _parse()
    if store is not None:
        if _msg_cb is not None:
            _msg_cb.to_pickle(f"./pkl/msg_cb{APPEND}.pkl")
        if _info_cb is not None:
            _info_cb.to_pickle(f"./pkl/info_cb{APPEND}.pkl")
        if _df_total is not None:
            _df_total.to_pickle(f"./pkl/df_total{APPEND}.pkl")
        if _df_eap is not None:
            _df_eap.to_pickle(f"./pkl/df_eap{APPEND}.pkl")
        if _cap_df is not None:
            _cap_df.to_pickle(f"./pkl/cap_df{APPEND}.pkl")

    return (_msg_cb, _info_cb, _df_total, _df_eap, _cap_df)

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
    df['classical_algo'] = [xv[0] if c else None for c, xv, yv in zip(df['hybrid'], df[x].str.split('_'), df[x])]
    df['pq_algo'] = ['_'.join(xv[1:]) if c else yv for c, xv, yv in zip(df['hybrid'], df[x].str.split('_'), df[x])]
    df['sec_level'] = [1 if a in PQ_L1_CURVES else 3 if a in PQ_L3_CURVES else 5 for a in df['pq_algo']]
    return df
if df_total is not None:
    df_total = add_sec_level(df_total, 'algo')
if df_eap is not None:
    df_eap = add_sec_level(df_eap, 'algo')
if msg_cb is not None:
    msg_cb = add_sec_level(msg_cb, 'groups')
    msg_cb['rutime'] = msg_cb['rutime'].astype(float)
    msg_cb['rstime'] = msg_cb['rstime'].astype(float)
