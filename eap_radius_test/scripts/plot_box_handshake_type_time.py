from plot import *
x = 'time_abs'

data=msg_cb[msg_cb['sec_level'] == 3].sort_values(x)
data = data[data['handshake_type_string'].isin(['client hello', 'server hello', 'finished'])]
data = data.groupby(['algo','run','handshake_type_string']).last().reset_index().sort_values(['algo','clock'])

order = data[data['handshake_type_string'] == 'finished'].groupby(['groups']).mean().reset_index().sort_values('time_abs')['groups']
data = data.rename({'handshake_type_string': 'TLS Record Type'}, axis=1)

ax = sns.boxplot(data=data, y='groups', x=x, hue='TLS Record Type', order=order)
ax.set(xlabel='Time in usec', ylabel='Algorithm')
plt.tight_layout()
savefig(__file__)
#plt.show()
