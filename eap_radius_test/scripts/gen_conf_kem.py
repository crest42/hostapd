import sys
from jinja2 import Environment, FileSystemLoader
from os import path, makedirs, getcwd

curves = []
curves_string = ""
PQ_L1_CURVES = ["bike1l1cpa", "bike1l1fo",
               "frodo640aes", "frodo640shake",
               "hqc128_1_cca2",
               "kyber512", "kyber90s512",
               "ntru_hps2048509",
               "lightsaber",
               "sidhp434", "sidhp503", "sikep434", "sikep503"]

PQ_L3_CURVES = ["bike1l3cpa", "bike1l3fo",
               "frodo976aes", "frodo976shake",
               "hqc192",
               "kyber768", "kyber90s768",
               "ntru_hps2048677", "ntru_hrss701",
               "saber",
               "sidhp610", "sikep610",
               "ntrulpr761", "sntrup761",]


PQ_L5_CURVES = ["frodo1344aes", "frodo1344shake",
                "hqc256_1_cca2", "hqc256_2_cca2", "hqc256_3_cca2",
                "kyber1024", "kyber90s1024",
                "ntru_hps4096821",
                "firesaber",
                "sidhp751", "sikep751"]

ECDH_L1_CURVES = ['p256']
ECDH_L3_CURVES = ['p384']
ECDH_L5_CURVES = ['p521']


for pq_curve in PQ_L1_CURVES:
    continue
    curves.append(pq_curve)
    for ecdh_curve in ECDH_L1_CURVES:
        c = f"{ecdh_curve}_{pq_curve}"
        curves.append(c)

for pq_curve in PQ_L3_CURVES:
    curves.append(pq_curve)
    for ecdh_curve in ECDH_L3_CURVES:
        c = f"{ecdh_curve}_{pq_curve}"
        curves.append(c)

for pq_curve in PQ_L5_CURVES:
    continue
    curves.append(pq_curve)
    for ecdh_curve in ECDH_L5_CURVES:
        c = f"{ecdh_curve}_{pq_curve}"
        curves.append(c)


#curves = curves + ['P-256', 'P-384', 'P-521']
curves = curves + ['P-384']
file_loader = FileSystemLoader('.') # directory of template file
env = Environment(loader=file_loader)
template = 'eap_tls_kem_template.conf.j2'
template = env.get_template(template) # load template file

BASE_DIR = '../confs'
CONF_DIR = f'{BASE_DIR}/kem'
if not path.exists(BASE_DIR):
    makedirs(BASE_DIR)

if not path.exists(CONF_DIR):
    makedirs(CONF_DIR)

for curve in curves:
    curves_string +=  f"{curve}:"
    filename = f"{CONF_DIR}/eap_tls_{curve}.conf"
    f = open(filename, 'w')
    output = template.render(curve=curve)
    f.write(output)
    f.close()


print(curves_string)
