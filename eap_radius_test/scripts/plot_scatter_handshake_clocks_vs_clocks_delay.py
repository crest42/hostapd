from plot import *
x = 'sum_len'

_0ms = pd.read_pickle('./pkl/msg_cb.pkl')
_0ms['delay'] = '0ms'
_1ms = pd.read_pickle('./pkl/msg_cb_1ms.pkl')
_1ms['delay'] = '1ms'
_10ms = pd.read_pickle('./pkl/msg_cb_10ms.pkl')
_10ms['delay'] = '10ms'
_100ms = pd.read_pickle('./pkl/msg_cb_100ms.pkl')
_100ms['delay'] = '100ms'
tidy = pd.concat([_0ms, _1ms,_10ms,_100ms])
tidy = add_sec_level(tidy,'groups')
tidy = tidy[tidy['sec_level'] == 3].groupby(['rnd']).last().reset_index().sort_values(x)


ax = sns.scatterplot(data=tidy, y='time_abs', x=x, hue='delay')
ax.set(xlabel='Bytes RX+TX', ylabel='Wall-Clock Runtime')
#plt.tight_layout()
#ax.set_xscale('log')
savefig(__file__)
#plt.show()
