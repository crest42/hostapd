import os
import subprocess
import time
import sys
from os import path, makedirs, getcwd
i = 0
KEM_CONF_DIR='../confs/kem/'
LOG_BASE_DIR='../logs'
LOG_DIR=f'{LOG_BASE_DIR}/kem'

if not path.exists(LOG_BASE_DIR):
    makedirs(LOG_BASE_DIR)

if not path.exists(LOG_DIR):
    makedirs(LOG_DIR)

dirlist = os.listdir(KEM_CONF_DIR)
stamp = int(time.time())
runs=1
for e in range(runs):
    for i, filename in enumerate(dirlist):
        if filename.endswith(".conf"):
            logfile = open(f'{LOG_DIR}/bench_{stamp}_{filename}_{e}.log','w')
            path = f'{KEM_CONF_DIR}{filename}'
            client = ("../eapol_test", "-c", path, "-s", "testing123")
            server = ("radiusd", "-f", '-l', "/dev/null", "-d", '/home/robin/git/freeradius-server/raddb_pq')
            print(' '.join(client))
            print(' '.join(server))
            sopen = subprocess.Popen(server, stdout=subprocess.DEVNULL)
            time.sleep(0.1)
            copen = subprocess.Popen(client, stdout=subprocess.DEVNULL,stderr=logfile)
            streamdata = copen.communicate()[0]
            rc = copen.wait()
            sopen.kill()
            logfile.flush()
            i += 1
#            time.sleep(1)
            if rc != 0:
                print(f"Error {path} aborted with {rc}")
                print(client)
                print(server)
                os.remove(f'{LOG_DIR}/bench_{stamp}_{filename}_{e}.log')
                sys.exit(rc)
                #break
            print(f"{filename} rc: {rc} {i}/{len(dirlist)}")
