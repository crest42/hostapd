import os
import subprocess
import time
import sys
i = 0
KEM_CONF_DIR='./confs/kem/'
dirlist = os.listdir(KEM_CONF_DIR)
stamp = int(time.time())
runs=100
for e in range(runs):
    for i, filename in enumerate(dirlist):
        if filename.endswith(".conf"):
            logfile = open(f'logs/kem/bench_{stamp}_{filename}_{e}.log','w')
            path = f'{KEM_CONF_DIR}{filename}'
            client = ("./eapol_test", "-c", path, "-s", "testing123")
            server = ("radiusd", "-f", '-l', "/dev/null", "-d", '/home/robin/git/freeradius-server/raddb_pq')
            sopen = subprocess.Popen(server, stdout=subprocess.DEVNULL)
            copen = subprocess.Popen(client, stdout=subprocess.DEVNULL,stderr=logfile)
            streamdata = copen.communicate()[0]
            rc = copen.wait()
            sopen.kill()
            logfile.flush()
            i += 1
#            time.sleep(1)
            if rc != 0:
                print(f"Error {path} aborted with {rc}")
                os.remove(f'logs/bench_{stamp}_{filename}_{e}.log')
                sys.exit(rc)
                #break
            print(f"{filename} rc: {rc} {i}/{len(dirlist)}")
