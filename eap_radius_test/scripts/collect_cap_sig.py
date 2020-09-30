import shlex
import pprint
import pandas as pd
import os
import pcapng
import scapy.all  # noqa
import scapy.packet
from scapy.layers.l2 import Ether
from pcapng.blocks import EnhancedPacket

LOG_BASE_DIR = '../logs/'
LOG_DIR = f'{LOG_BASE_DIR}/sig/'

dirlist = os.listdir(LOG_DIR)
res = []
for i, l in enumerate(dirlist):
    if not l.endswith('.cap'):
        continue
    print(f'Parsing log {i}/{len(dirlist)}')
    print(l)
    sig = l.split('_')[:-1][4:]
    sig = '_'.join(sig).split('.')[:-1][0]
    packets = scapy.all.rdpcap(f'{LOG_DIR}/{l}')
    for x, packet in enumerate(packets):
        #print(x)
        #print(packet.show())
        if packet.haslayer(scapy.all.Radius):
            for Radius in packet:
                for attribute in Radius.attributes:
                    d = {'sig': sig}
                    d['type'] = int(attribute.type)
                    d['len'] = int(attribute.len)
                    res.append(d)

df = pd.DataFrame(res)
group = df.groupby(['sig','type'])
sum = group.sum().reset_index()
print(df)
