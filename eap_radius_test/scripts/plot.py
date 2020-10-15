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

def get_real_name(name):
    return f"{'.'.join(name.split('.')[:-1])}.pdf"

def savefig(name):
    path = f"{PLOT_PATH}/{get_real_name(name)}"
    print(path)
    plt.savefig(path)
