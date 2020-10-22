import seaborn as sns
from collect_kem import *
import matplotlib.pyplot as plt
import matplotlib as mpl
#mpl.rcParams['text.usetex'] = True
colors = sns.color_palette('Paired')
colors = colors[0:10] + colors[11:]
sns.set(context='paper', palette=colors)
sns.set_style(sns.axes_style('ticks'), {'axes.grid': True})

PLOT_PATH='/home/robin/git/ma/loes20/Dokumentation/Latex/Bilder/'

cap_df = add_sec_level(cap_df, 'algo')
frames = cap_df[['algo', 'pq_algo', 'classical_algo','hybrid', 'sec_level','run','time', 'frame_nr', 'frame_count', 'frame_len', 'rad_len']].groupby(['algo','run','frame_count']).first().reset_index()
rad_avp = cap_df[['algo', 'time', 'run', 'frame_nr', 'frame_count', 'avp_count' ,'rad_avp_len', 'eap.len']].groupby(['algo','run','frame_count','avp_count']).first().groupby(['algo', 'run', 'frame_count']).sum().reset_index()
records = cap_df.fillna(0)[['algo', 'time', 'run', 'frame_nr', 'frame_count', 'avp_count','record_count' ,'tls.record.length']].groupby(['algo','run','frame_count','avp_count','record_count']).first().groupby(['algo', 'run', 'frame_count']).sum().reset_index()

merge = frames
merge['rad_avp_len'] = rad_avp['rad_avp_len']
merge['eap.len'] = rad_avp['eap.len']
merge['tls.record.length'] = records['tls.record.length']
merge = merge[merge['sec_level'] == 3]
def get_real_name(name):
    return f"{'.'.join(name.split('.')[:-1])}.pdf"

def savefig(name):
    path = f"{PLOT_PATH}/{get_real_name(name)}"
    print(path)
    plt.savefig(path)
