import os
import subprocess
import time
import sys
i = 0
dirlist = os.listdir('./confs')
stamp = int(time.time())
runs=2
for e in range(runs):
    for i, filename in enumerate(dirlist):
        if filename.endswith(".conf"):
            logfile = open(f'logs/bench_{stamp}_{filename}_{e}.log','w')
            path = f'./confs/{filename}'
            args = ("./eapol_test", "-c", path, "-s", "testing123")
            popen = subprocess.Popen(args, stdout=subprocess.DEVNULL,stderr=logfile)
            streamdata = popen.communicate()[0]
            rc = popen.wait()
            logfile.flush()
            i += 1
            time.sleep(1)
            if rc != 0:
                print(f"Error {path} aborted with {rc}")
                os.remove(f'logs/bench_{stamp}_{filename}_{e}.log')
                sys.exit(rc)
                #break
            print(f"{filename} rc: {rc} {i}/{len(dirlist)}")