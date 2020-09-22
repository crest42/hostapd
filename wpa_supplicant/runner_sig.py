import os
import subprocess
import time
import sys
i = 0
HOSTAPD_CONF_DIR='./confs/sig/hostapd/'
RADDB_CONF_DIR='./confs/sig/raddb/'
LOG_DIR='logs/sig/'
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)  
h_dirlist = os.listdir(HOSTAPD_CONF_DIR)
stamp = int(time.time())

runs=1
for e in range(runs):
    for i, filename in enumerate(h_dirlist):
        if filename.endswith(".conf"):
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
            logfile_name = f'logs/sig/bench_{stamp}_{filename}_{e}.log'
            logfile = open(logfile_name,'w')
            hconfig = f'{HOSTAPD_CONF_DIR}/{filename}'
            client = ("./eapol_test", "-c", hconfig, "-s", "testing123")
            server = ("radiusd", "-f", '-l', "/dev/null", "-d", raddb_conf)
            sopen = subprocess.Popen(server, stdout=subprocess.DEVNULL)
            copen = subprocess.Popen(client, stdout=subprocess.DEVNULL,stderr=logfile)
            streamdata = copen.communicate()[0]
            rc = copen.wait()
            sopen.kill()
            logfile.flush()
            i += 1
#            time.sleep(1)
            if rc != 0:
                print(f"Error {filename} aborted with {rc}")
                print(client)
                print(server)
                os.remove(logfile_name)
                sys.exit(rc)
                #break
            print(f"{filename} rc: {rc} {i}/{len(h_dirlist)}")

