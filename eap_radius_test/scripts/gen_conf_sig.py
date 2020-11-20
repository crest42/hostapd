import sys
import subprocess
import shutil
from os import path, makedirs, getcwd
from jinja2 import Environment, FileSystemLoader

file_loader = FileSystemLoader('.') # directory of template file
env = Environment(loader=file_loader)
TEMPLATE_PEER = env.get_template('eap_tls_sig_template.conf.j2') # load template file
TEMPLATE_SUPP = env.get_template('raddb_template/mods-enabled/eap') # load template file
OPENSSL_DIR = '/home/robin/git/openssl-1.1.1/apps/'
RADDB_TEMPLATE_DIR='raddb_template/'
BASE_DIR = f'{getcwd()}/../confs/'
SIG_DIR = f'{BASE_DIR}/sig'
CERTDIR = f"{BASE_DIR}/cert"
SUPP_CONF_DIR = f"{SIG_DIR}/hostapd"
RADDB_DIR = f"{SIG_DIR}/raddb/"

if not path.exists(CERTDIR):
    makedirs(CERTDIR)  
if not path.exists(SIG_DIR):
    makedirs(SIG_DIR) 
if not path.exists(SUPP_CONF_DIR):
    makedirs(SUPP_CONF_DIR)  
if not path.exists(RADDB_DIR):
    makedirs(RADDB_DIR)  

def create_cert(sig):
    certfile = f"{CERTDIR}/eap_tls_{sig}.pem"
    keyfile = f"{CERTDIR}/eap_tls_{sig}.key"
    if not (path.exists(certfile) and path.exists(keyfile)):
        newcert = f'{OPENSSL_DIR}/openssl req -x509 -new -newkey {sig} -keyout {keyfile} -out {certfile} -nodes -subj "/CN=oqstest CA" -days 365 -config {OPENSSL_DIR}/openssl.cnf'
        popen = subprocess.run(newcert, shell = True)
        rc = popen.returncode
        if rc != 0:
            print(f"Error {newcert} aborted with {rc}")
            sys.exit(rc)
    return (certfile, keyfile)


def create_wpa_config(certfile, keyfile, sig, template):
    output = template.render(certfile=certfile, keyfile=keyfile)
    conffile = f"{SUPP_CONF_DIR}/eap_tls_{sig}.conf"
    f = open(conffile, 'w')
    f.write(output)
    f.close()

def create_raddb(certfile, keyfile, sig, template):
    raddb = f'{RADDB_DIR}/raddb_{sig}'
    eap_config = f'{raddb}/mods-enabled/eap'
    if path.exists(raddb):
        shutil.rmtree(raddb)
    shutil.copytree(RADDB_TEMPLATE_DIR, raddb)
    f = open(eap_config, 'w')
    f.write(template.render(certfile=certfile, keyfile=keyfile))
    f.close()

sigs = []
PQ_L1_SIG = []
#PQ_L1_SIG = ['dilithium2','falcon512','picnicl1full','picnic3l1','rainbowIaclassic' ,'sphincsharaka128frobust']
#PQ_L1_SIG_DISABLED = ['picnicl1fs','picnicl1ur', 'rainbowIacyclic','rainbowIacycliccompressed','sphincsharaka128fsimple','sphincsharaka128srobust','sphincsharaka128ssimple','sphincssha256128frobust','sphincssha256128fsimple','sphincssha256128srobust','sphincssha256128ssimple','sphincsshake256128frobust','sphincsshake256128fsimple','sphincsshake256128srobust', 'sphincsshake256128ssimple']
PQ_L3_SIG = ['dilithium4','picnic3l3','rainbowIIIcclassic', 'rainbowIIIccyclic', 'rainbowIIIccycliccompressed','sphincsharaka192frobust','sphincsharaka192fsimple','sphincsharaka192srobust','sphincsharaka192ssimple','sphincssha256192frobust','sphincssha256192fsimple','sphincssha256192srobust','sphincssha256192ssimple','sphincsshake256192frobust', 'sphincsshake256192fsimple', 'sphincsshake256192srobust', 'sphincsshake256192ssimple']
PQ_L3_SIG_DISABLED = ['dilithium3']


PQ_L5_SIG = []
PQ_L5_SIG = ['falcon1024']
#PQ_L5_SIG_DISABLED = ['rainbowVcclassic', 'picnic3l5','rainbowVccyclic', 'rainbowVccycliccompressed','sphincsharaka256frobust','sphincsharaka256fsimple','sphincsharaka256srobust','sphincsharaka256ssimple','sphincssha256256frobust','sphincssha256256fsimple','sphincssha256256srobust','sphincssha256256ssimple','sphincsshake256256frobust','sphincsshake256256fsimple', 'sphincsshake256256srobust','sphincsshake256256ssimple']
#CLASSIC_L1_SIG = ['rsa3072','p256']
CLASSIC_L3_SIG = ['p384']
CLASSIC_L5_SIG = ['p521']

for pq_sig in PQ_L1_SIG:
    sigs.append(pq_sig)
    for classical_sig in CLASSIC_L1_SIG:
        c = f"{classical_sig}_{pq_sig}"
        sigs.append(c)



for pq_sig in PQ_L3_SIG:
    sigs.append(pq_sig)
    for classical_sig in CLASSIC_L3_SIG:
        c = f"{classical_sig}_{pq_sig}"
        sigs.append(c)

for pq_sig in PQ_L5_SIG:
    sigs.append(pq_sig)
    for classical_sig in CLASSIC_L5_SIG:
        c = f"{classical_sig}_{pq_sig}"
        sigs.append(c)


sigs = sigs + ['ED25519']

for sig in sigs:
    (certfile, keyfile) = create_cert(sig)
    create_wpa_config(certfile, keyfile, sig, TEMPLATE_PEER)
    create_raddb(certfile, keyfile, sig, TEMPLATE_SUPP)
