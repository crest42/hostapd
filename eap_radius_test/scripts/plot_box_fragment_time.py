from plot import *

msg_cb = pd.read_pickle('./pkl/sig/msg_cb_fragment_size.pkl')
msg_cb_10 = pd.read_pickle('./pkl/sig/msg_cb_fragment_size_10ms.pkl')

msg_cb['mtu'] = msg_cb['algo'].str.split('_', expand=True)[1]
msg_cb['mtu'] = msg_cb['mtu'].astype(int)
msg_cb_10['mtu'] = msg_cb['algo'].str.split('_', expand=True)[1]
msg_cb_10['mtu'] = msg_cb['mtu'].astype(int)
msg_cb['delay'] = 0
msg_cb_10['delay'] = 10
merge = pd.concat([msg_cb, msg_cb_10], ignore_index=True)
merge['mtu'] //= 1000
merge = merge.groupby(['algo','run', 'delay']).last().reset_index()
g = sns.FacetGrid(merge.rename({'time_abs': 'Wall-Clock Runtime in nsec', 'mtu': 'MTU Size in kB'}, axis=1), col='delay', sharey=False)
g.map_dataframe(sns.boxplot, y='Wall-Clock Runtime in nsec', x='MTU Size in kB')
g.set_axis_labels("MTU Size in kB", "Wall-Clock Runtime in nsec")
#sns.boxplot(data=merge, x='mtu', y ='time_abs', hue='delay')
plt.tight_layout()
savefig(__file__)
#plt.show()

