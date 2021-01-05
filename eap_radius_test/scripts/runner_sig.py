import os
import subprocess
import time
import sys
import scapy.all
import signal

LOG_BASE_DIR = '../logs'
HOSTAPD_CONF_DIR = '../confs/sig/hostapd/'
RADDB_CONF_DIR = '../confs/sig/raddb/'
LOG_DIR = f'{LOG_BASE_DIR}/sig_{sys.argv[1]}/'
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)  
h_dirlist = os.listdir(HOSTAPD_CONF_DIR)
stamp = int(time.time())

def get_raddb_conf(filename):
    split = filename.split('_')
    raddb_conf = f'{RADDB_CONF_DIR}/raddb_'
    if len(split) == 3:
        _ = split[-1].split('.')[0]
        raddb_conf += _
    elif len(split) == 4:
        _ = split[-2] + '_' + split[-1].split('.')[0]
        raddb_conf += _
    else:
        print(f"invalid split: '{split}'")
        sys.exit(1)
    if not os.path.exists(raddb_conf):
        print(f"Invalid raddb '{raddb_conf}'")
        sys.exit(1)
    return raddb_conf


runs=100
for e in range(1,runs):
    for i, filename in enumerate(h_dirlist):
        if filename.endswith(".conf"):
            raddb_conf = get_raddb_conf(filename)
            logfile_name = f'{LOG_DIR}/bench_{stamp}_{filename}_{e}.log'
            capfile_name = f'{LOG_DIR}/bench_{stamp}_{filename}_{e}.cap'
            logfile = open(logfile_name,'w')
            hconfig = f'{HOSTAPD_CONF_DIR}/{filename}'
            client = ("../eapol_test", "-c", hconfig, "-s", "testing123")
            server = ("radiusd", "-f", '-l', "stdout", "-d", raddb_conf)
            tshark = ("dumpcap", "-q", "-i", "lo", "-w", capfile_name)
            print(' '.join(client))
            print(' '.join(server))
            print(' '.join(tshark))
            sopen = None
            copen = None
            tshark_open = None
            try:
                tshark_open = subprocess.Popen(tshark, stderr=subprocess.PIPE)
                out = []
                for j, line in enumerate(iter(tshark_open.stderr.readline, '')):
                    out.append(line.decode('utf-8').rstrip())
                    if out[-1].endswith(f"File: {capfile_name}"):
                        break
                    elif out[-1] == '':
                        err = '\n'.join(out)
                        print(f"Error while waiting for tshark: {err}")
                        sys.exit(1)
                sopen = subprocess.Popen(server, stdout=subprocess.PIPE)
                out = []
                for j, line in enumerate(iter(sopen.stdout.readline, '')):
                    out.append(line.decode('utf-8').rstrip())
                    if out[-1].endswith('Info: Ready to process requests'):
                        break
                    elif out[-1] == '':
                        err = '\n'.join(out)
                        print(f"Error while waiting for radiusd: {err}")
                        sys.exit(1)
                copen = subprocess.Popen(client, stderr=subprocess.DEVNULL,stdout=logfile)
                streamdata = copen.communicate()[0]
                rc = copen.wait()
                sopen.send_signal(signal.SIGINT)
                sopen.wait()
                time.sleep(0.5)
                tshark_open.send_signal(signal.SIGINT)
                tshark_open.wait()
                logfile.flush()
                if rc != 0:
                    print(f"Error {filename} aborted with {rc}")
                    os.remove(logfile_name)
                    sys.exit(rc)
                print(f"{filename} rc: {rc} {i}/{len(h_dirlist)} run: {e}/{runs}")
            except Exception as ex:
                print(f"Unexpected error '{ex}', kill childs")
                #if tshark_open is not None:
                #    tshark_open.kill()
                #    tshark_open.wait()
                if sopen is not None:
                    sopen.kill()
                    sopen.wait()
                if copen is not None:
                    sopen.kill()
                    sopen.wait()
                sys.exit(1)
