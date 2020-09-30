import os
import subprocess
import time
import sys
import scapy.all

HOSTAPD_CONF_DIR='../confs/sig/hostapd/'
RADDB_CONF_DIR='../confs/sig/raddb/'
LOG_DIR='../logs/sig/'
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


runs=3
for e in range(1,runs):
    for i, filename in enumerate(h_dirlist):
        if filename.endswith(".conf"):
            raddb_conf = get_raddb_conf(filename)
            logfile_name = f'{LOG_DIR}/bench_{stamp}_{filename}_{e}.log'
            capfile_name = f'{LOG_DIR}/bench_{stamp}_{filename}_{e}.cap'
            logfile = open(logfile_name,'w')
            hconfig = f'{HOSTAPD_CONF_DIR}/{filename}'
            client = ("../eapol_test", "-c", hconfig, "-s", "testing123")
            server = ("radiusd", "-f", '-l', "/dev/null", "-d", raddb_conf)
            t = scapy.all.AsyncSniffer(iface='lo', filter="udp port 1812")
            t.start()
            sopen = subprocess.Popen(server, stdout=subprocess.DEVNULL)
            time.sleep(0.2)
            copen = subprocess.Popen(client, stdout=subprocess.DEVNULL,stderr=logfile)
            streamdata = copen.communicate()[0]
            rc = copen.wait()
            sopen.kill()
            time.sleep(1)
            scapy.all.wrpcap(capfile_name,t.stop())
            logfile.flush()
            if rc != 0:
                print(f"Error {filename} aborted with {rc}")
                print(' '.join(client))
                print(' '.join(server))
                os.remove(logfile_name)
                sys.exit(rc)
                #break
            print(f"{filename} rc: {rc} {i}/{len(h_dirlist)}")
