import os
import subprocess
import time
import sys
import signal
from os import path, makedirs, getcwd

i = 0
KEM_CONF_DIR='../confs/kem/'
LOG_BASE_DIR='../logs'
LOG_DIR=f'{LOG_BASE_DIR}/kem_{sys.argv[1]}'

if not path.exists(LOG_BASE_DIR):
    makedirs(LOG_BASE_DIR)

if not path.exists(LOG_DIR):
    makedirs(LOG_DIR)

dirlist = os.listdir(KEM_CONF_DIR)
stamp = int(time.time())
RUNS=100
for e in range(RUNS):
    for i, filename in enumerate(dirlist):
        if filename.endswith(".conf"):
            logfile = open(f'{LOG_DIR}/bench_{stamp}_{filename}_{e}_inst.log','w')
            #logfile_t = open(f'{LOG_DIR}/bench_{stamp}_{filename}_{e}_time.log','w')
            capfile_name = f'{LOG_DIR}/bench_{stamp}_{filename}_{e}_cap.cap'
            path = f'{KEM_CONF_DIR}{filename}'
            client = ("../eapol_test", "-c", path, "-s", "testing123")
            server = ("radiusd", "-f", '-l', "stdout", "-d", '/home/robin/git/freeradius-server/raddb_pq')
            tshark = ("dumpcap", '-q', "-i", "lo", "-w", capfile_name)
            print(' '.join(client))
            print(' '.join(server))
            print(' '.join(tshark))
            tshark_open = None
            sopen = None
            copen = None
            try:
                tshark_open = subprocess.Popen(tshark, stderr=subprocess.PIPE)
                out = []
                for j, line in enumerate(iter(tshark_open.stderr.readline,'')):
                    out.append(line.decode('utf-8').rstrip())
                    if out[-1].endswith(f"File: {capfile_name}"):
                        break
                    elif out[-1] == '':
                        err = '\n'.join(out)
                        print(f"Error while waiting for successfull tshark startup {err}")
                        sys.exit(1)
                sopen = subprocess.Popen(server, stdout=subprocess.PIPE)
                out = []
                for j, line in enumerate(iter(sopen.stdout.readline,'')):
                    out.append(line.decode('utf-8').rstrip())
                    if out[-1].endswith('Info: Ready to process requests'):
                        break
                    elif out[-1] == '':
                        err = '\n'.join(out)
                        print(f"Error while waiting for successfull freeradius startup {err}")
                        sys.exit(1)
                copen = subprocess.Popen(client, stdout=logfile, stderr=subprocess.DEVNULL)
                streamdata = copen.communicate()[0]
                rc = copen.wait()
                sopen.send_signal(signal.SIGINT)
                sopen.wait()
                time.sleep(0.5)
                tshark_open.send_signal(signal.SIGINT)
                tshark_open.wait()
                logfile.flush()

                if rc != 0:
                    print(f"Error in executing eapol_test. RC: {rc} Log: {logfile}")
                    sys.exit(rc)
                print(f"{filename} rc: {rc} {i}/{len(dirlist)} Run {e}/{RUNS}")
                print()
            except Exception as ex:
                print(f"Got exception '{ex}', Terminate Childs")
                if tshark_open is not None:
                    tshark_open.kill()
                    tshark_open.wait()
                if sopen is not None:
                    sopen.kill()
                    sopen.wait()
                if copen is not None:
                    copen.kill()
                    copen.wait()
                sys.exit(1)


print("SUCCESSFULL RUN")
