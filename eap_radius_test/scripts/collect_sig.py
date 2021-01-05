import shlex
import time
import os
import sys
import subprocess
import json
import pprint
import psutil
import numpy as np
import ray
import pandas as pd
APPEND = '0ms'
if len(sys.argv) == 3:
  APPEND = sys.argv[2]
LOG_BASE_DIR = '../logs/'
LOG_DIR = f'{LOG_BASE_DIR}/sig_{APPEND}'

def usage():
     process = psutil.Process(os.getpid())
     return process.memory_info()

def parse_algo(l):
    split = l.split('_')
    ts = split[1]
    run = split[-1].split('.')[0]
    algo = '_'.join(split[4:-1]).split('.')[0]
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
    return {'run': run, 'ts': ts, 'type': s[0], 'algo': algo,  'clock': s[1]}

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
    s = time.clock_gettime(time.CLOCK_MONOTONIC)
    dfs = []
    tshark = ('/home/robin/git/wireshark/build/run/tshark', '-n', '-2', '-r', capfile, '-T', 'json', '--no-duplicate-keys')
    o = subprocess.Popen(tshark, stdout=subprocess.PIPE)
    packets = json.loads(o.communicate()[0])
    pkt_count = 0
    append = []
    #columns = [('algo', str), ('ts', int), ('run', int), ('time', int),
    #           ('time_delta',float), ('frame_nr', int), ('frame_len',int),
    #           ('rad_len', int), ('rad_code', int), ('rad_id', int),
    #           ('avp_count', int), ('rad_avp_t',int),
    #           ('rad_avp_len',int), ('eap.id',int), ('eap.code',int),
    #           ('eap.len',int), ('eap.type',int), ('tls_record_count',int),('tls_record_length', int)]
    #dtypes = np.dtype(columns)
    #tmp_df = pd.DataFrame(np.empty(len(packets)*10, dtype=dtypes))
    #tmp_df.at[:,'algo'] = algo 
    #tmp_df.at[:,'ts'] = ts
    #tmp_df.at[:,'run'] = run
    index = 0
    rows=[]
    runtime = time.clock_gettime(time.CLOCK_MONOTONIC) - s
    print(f"Head: {runtime}")
    s = time.clock_gettime(time.CLOCK_MONOTONIC)
    for _x, packet in enumerate(packets):
        d = {}
        packet = packet['_source']
        if 'radius' not in packet['layers']:
            continue
        frame = packet['layers']['frame']
        radius = packet['layers']['radius']
        _al = len(radius['Attribute Value Pairs']['radius.avp_tree'])
        #tmp_df.at[index:,'time'] = frame['frame.time']
        #tmp_df.at[index:,'time_delta'] = frame['frame.time_delta']
        #tmp_df.at[index:,'frame_nr'] = frame['frame.number']
        #tmp_df.at[index:,'frame_len'] = frame['frame.len']
        #tmp_df.at[index:,'rad_len'] = radius['radius.length']
        #tmp_df.at[index:,'rad_code'] = radius['radius.code']
        #tmp_df.at[index:,'rad_id'] = radius['radius.id']
        for avp_count, x in enumerate(radius['Attribute Value Pairs']['radius.avp_tree']):
            eap_type = 0
            eap_code = 0
            eap_id = 0
            eap_len = 0
            tls_record_count = 0
            tls_record_length = 0
            index += 1
            _d = {}
            #tmp_df.at[index,'avp_count'] = avp_count
            if 'eap' in x:
                    if 'eap.type' in x['eap']:
                        eap_type = int(x['eap']['eap.type'])
                    else:
                        eap_type = 0
                    eap_code = int(x['eap']['eap.code'])
                    eap_id = int(x['eap']['eap.id'])
                    eap_len = int(x['eap']['eap.len'])
                    if _x == 0:
                        assert(eap_code == 2 and eap_type == 1)
                    if _x == len(packets)-1:
                        assert(eap_code == 3)
                    if 'tls' in x['eap']:
                        tls_records = []
                        if not isinstance(x['eap']['tls'],str):
                            for _k in x['eap']['tls']:
                                if _k == 'tls.record':
                                    records = x['eap']['tls'][_k]
                                    if isinstance(records, dict):
                                        records = [records]
                                    for i, record in enumerate(records):
                                        assert('tls.record.length' in record)
                                        tls_record_length += int(record['tls.record.length'])
                                        tls_record_count += 1
                                elif _k == 'Ignored Unknown Record':
                                    assert(False)
                                    pass
                                else:
                                    print(d['frame_nr'])
                                    pprint.pprint(x[k])
            rows.append({'algo': algo, 
                         'ts': ts,
                         'run': run,
                         'time': frame['frame.time'],
                         'time_delta': frame['frame.time_delta'],
                         'frame_nr': frame['frame.number'],
                         'frame_len': frame['frame.len'],
                         'rad_len': radius['radius.length'],
                         'rad_code': radius['radius.code'],
                         'rad_id': radius['radius.id'],
                         'rad_avp_count': avp_count,
                         'rad_avp_type': x['radius.avp.type'],
                         'rad_avp_len': x['radius.avp.length'],
                         'eap.id': eap_id,
                         'eap.code': eap_code,
                         'eap.len': eap_len,
                         'eap.type': eap_type,
                         'tls_record_count': tls_record_count,
                         'tls_record_length': tls_record_length})
            index += 1
    runtime = time.clock_gettime(time.CLOCK_MONOTONIC) - s
    print(f"Loop: {runtime}")
    return pd.DataFrame(rows), len(rows)

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
    del log
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
    _cap_df['tls_record_length'] = _cap_df['tls_record_length'].astype(float)
    return _cap_df

def beautify(bench, time, cap_df):
    _msg_cb = None
    _info_cb = None
    _df_total = None
    _df_eap = None
    if len(bench) > 0:
        bench_df = pd.DataFrame(bench)
        if len(bench_df) > 0:
            _msg_cb = bench_df[bench_df['type'] == 'tls_msg_cb_bench'].copy().dropna(axis='columns')
            _msg_cb = beautify_msg(_msg_cb)

        if len(bench_df) > 0:
            _info_cb = bench_df[bench_df['type'] == 'tls_info_cb_bench'].copy().dropna(axis='columns')
            _info_cb = beautify_info(_info_cb)

    if len(time) > 0:
        time_df = pd.DataFrame(time)
        if len(time_df) > 0:
            _df_total, _df_eap = beautify_time(time_df)

    if len(cap_df) > 0:
        cap_df = beautify_cap(cap_df)

    return _msg_cb, _info_cb, _df_total, _df_eap, cap_df

def _parse(cap_df, c, _min=0, _max=None):
    bench = []
    _time = []
    dfs = []
    print(c)
    dirlist = os.listdir(LOG_DIR)
    if _max is None:
        _max=len(dirlist)
    for i, l in enumerate(dirlist):
        if i < _min or i > _max:
            continue
        print(f'Parsing log {i}/{len(dirlist)}: {l}')
        algo, ts, run = parse_algo(l)
        if l.endswith('.log'):
            if c:
                continue
            instfile = f'{LOG_DIR}/{l}'
            a = []
            b = []
            a, b = parse_inst(instfile, algo, ts, run)
            bench += a
            _time += b
        elif l.endswith('.cap'):
            if not c:
                continue
            capfile = f'{LOG_DIR}/{l}'
            old_count = len(cap_df)
            s = time.clock_gettime(time.CLOCK_MONOTONIC)
            _df, nrows = parse_cap(capfile, algo, ts, run)
            runtime = time.clock_gettime(time.CLOCK_MONOTONIC) - s
            dfs.append(_df)
            print(f"Time per row: {runtime/nrows} ({runtime}/{nrows})")

        else:
            print(f"Error unknown log {l}")
            sys.exit(1)
    if c:
        return beautify(bench, _time, pd.concat(dfs))
    else:
        return beautify(bench, _time, pd.DataFrame())


def main(cap_df, load=None, store=None, cap=False):
    if load is not None:
        _msg_cb = None
        _info_cb = None
        _df_total = None
        _df_eap = None
        if not cap:
            _msg_cb = pd.read_pickle(f"./pkl/sig/msg_cb_{APPEND}.pkl")
        if not cap:
            _info_cb = pd.read_pickle(f"./pkl/sig/info_cb_{APPEND}.pkl")
        if not cap:
            _df_total = pd.read_pickle(f"./pkl/sig/df_total_{APPEND}.pkl")
        if not cap:
            _df_eap = pd.read_pickle(f"./pkl/sig/df_eap_{APPEND}.pkl")
        if cap:
            cap_df = pd.read_pickle(f"./pkl/sig/cap_df_{APPEND}.pkl")
        return (_msg_cb, _info_cb, _df_total, _df_eap, cap_df)
    (_msg_cb, _info_cb, _df_total, _df_eap, cap_df) = _parse(cap_df, cap)
    print("Parsing Done store Data")
    if store is not None:
        if _msg_cb is not None:
            print(f"./pkl/sig/msg_cb_{APPEND}.pkl")
            _msg_cb.to_pickle(f"./pkl/sig/msg_cb_{APPEND}.pkl")
        if _info_cb is not None:
            print(f"./pkl/sig/info_cb_{APPEND}.pkl")
            _info_cb.to_pickle(f"./pkl/sig/info_cb_{APPEND}.pkl")
        if _df_total is not None:
            print(f"./pkl/sig/df_total_{APPEND}.pkl")
            _df_total.to_pickle(f"./pkl/sig/df_total_{APPEND}.pkl")
        if _df_eap is not None:
            print(f"./pkl/sig/df_eap_{APPEND}.pkl")
            _df_eap.to_pickle(f"./pkl/sig/df_eap_{APPEND}.pkl")
        if len(cap_df) > 0:
            print(f"./pkl/sig/cap_df_{APPEND}.pkl")
            cap_df.to_pickle(f"./pkl/sig/cap_df_{APPEND}.pkl")

    return (_msg_cb, _info_cb, _df_total, _df_eap, cap_df)

(msg_cb, info_cb, df_total, df_eap, cap_df) = None, None, None, None, None
cap_df = pd.DataFrame(columns=['algo', 'ts', 'run', 'time', 'time_delta', 'frame_nr', 'frame_len',
       'frame_count', 'src', 'dst', 'rad_len', 'rad_code', 'rad_id',
       'avp_count', 'rad_avp_t', 'rad_avp_len', 'eap.id', 'eap.code',
       'eap.len', 'eap.type', 'tls_record_length', 'tls_record_count'])
       
if __name__ == '__main__':
    load  = None
    store = None
    cap   = None
    if len(sys.argv) > 1:
        if sys.argv[1] == 'load':
            load = True
        if sys.argv[1] == 'store':
            store = True
        if len(sys.argv) > 2:
            if sys.argv[2] == 'cap':
                cap = True
            else:
                cap = False
    else:
        sys.exit(-1)
    (msg_cb, info_cb, df_total, df_eap, cap_df) = main(cap_df, load=load, store=store, cap=cap)

def get_inst_cb():
    return main(cap_df, load='load', cap=False)

def get_cap_df():
    return main(cap_df, load='load', cap=True)[4]

PQ_L1_SIG = ['dilithium3']
PQ_L3_SIG = ['dilithium4','picnic3l3','rainbowIIIcclassic', 'rainbowIIIccyclic', 'rainbowIIIccycliccompressed','sphincsharaka192frobust','sphincsharaka192fsimple','sphincsharaka192srobust','sphincsharaka192ssimple','sphincssha256192frobust','sphincssha256192fsimple','sphincssha256192srobust','sphincssha256192ssimple','sphincsshake256192frobust', 'sphincsshake256192fsimple', 'sphincsshake256192srobust', 'sphincsshake256192ssimple', 'P-384','ED25519']
PQ_L5_SIG = ['falcon1024', 'P-521']

def add_sec_level(df, x):
    df['hybrid'] = np.where(df[x].str.startswith('p256_') | df[x].str.startswith('p384_') | df[x].str.startswith('p521_'), True, False)
    df['classical_algo'] = [xv[0] if c else None for c, xv, yv in zip(df['hybrid'], df[x].str.split('_'), df[x])]
    df['pq_algo'] = ['_'.join(xv[1:]) if c else yv for c, xv, yv in zip(df['hybrid'], df[x].str.split('_'), df[x])]
    df['sec_level'] = [1 if a in PQ_L1_SIG else 3 if a in PQ_L3_SIG else 5 for a in df['pq_algo']]
    return df

