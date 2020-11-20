import seaborn as sns
from scipy import stats
from collect_sig import *
import matplotlib.pyplot as plt
import matplotlib as mpl
#mpl.rcParams['text.usetex'] = True
colors = sns.color_palette('Paired')
colors = colors[0:10] + colors[11:]
sns.set(context='paper', palette=colors)
sns.set_style(sns.axes_style('ticks'), {'axes.grid': True})

PLOT_PATH='/home/robin/git/ma/loes20/Dokumentation/Latex/Bilder/'

def get_merged_cap_df():
    cap_df = get_cap_df()
    frames = cap_df[['algo', 'run','time', 'frame_nr', 'frame_count', 'frame_len', 'rad_len']].groupby(['algo','run','frame_count']).first()
    rad_avp = cap_df[['algo', 'time', 'run', 'frame_nr', 'frame_count', 'avp_count' ,'rad_avp_len', 'eap.len']].groupby(['algo','run','frame_count','avp_count']).first().groupby(['algo', 'run', 'frame_count']).sum()
    records = cap_df[['algo', 'time', 'run', 'frame_nr', 'frame_count', 'avp_count','record_count' ,'tls.record.length']].dropna().groupby(['algo','run','frame_count','avp_count','record_count']).first().groupby(['algo', 'run', 'frame_count']).sum()

    frames['rad_avp_len'] = rad_avp['rad_avp_len']
    frames['eap.len'] = rad_avp['eap.len']
    frames['tls.record.length'] = records['tls.record.length']
    return add_sec_level(frames.reset_index(), 'algo')

def get_real_name(name):
    return f"{'.'.join(name.split('.')[:-1])}.pdf"

def savefig(name):
    path = f"{PLOT_PATH}/{get_real_name(name)}"
    print(path)
    plt.savefig(path)


def ttest(data1, data2, x, y='algo'):
    algos = set(data1[y]).intersection(set(data2[y]))
    res  = {}
    for algo in algos:
        set1 = np.array(data1[data1[y] == algo][x])
        set2 = np.array(data2[data2[y] == algo][x])
        res[algo] = stats.ttest_ind(set1,set2)
    return res

