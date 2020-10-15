from plot import *
x = 'wct'


_1ms = pd.read_pickle('./pkl/df_total_1ms.pkl')
_1ms['delay'] = '1ms'
_10ms = pd.read_pickle('./pkl/df_total_10ms.pkl')
_10ms['delay'] = '10ms'
_100ms = pd.read_pickle('./pkl/df_total_100ms.pkl')
_100ms['delay'] = '100ms'
tidy = pd.concat([_1ms,_10ms,_100ms])
tidy = add_sec_level(tidy,'algo')
tidy = tidy[tidy['sec_level'] == 3].groupby(['ts','algo','run']).last().reset_index().sort_values(x)
ax = sns.boxplot(data=tidy, y='algo', x=x, hue='delay')
ax.set(xlabel='Wall-Clock Runtime', ylabel='Algorithm')
plt.tight_layout()
ax.set_xscale('log')
plt.show()
