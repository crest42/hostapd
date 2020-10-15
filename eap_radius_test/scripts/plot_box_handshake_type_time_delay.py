from plot import *
x = 'time_abs'
msg_cb = pd.read_pickle('./pkl/msg_cb_10ms.pkl')
add_sec_level(msg_cb, 'groups')
data=msg_cb[msg_cb['sec_level'] == 3].sort_values(x)
data = data[data['handshake_type_string'].isin(['client hello', 'server hello', 'finished'])]
order = data[data['handshake_type_string'] == 'finished'].groupby(['groups']).mean().reset_index().sort_values('time_abs')['groups']
ax = sns.boxplot(data=data, y='groups', x=x, hue='handshake_type_string', order=order)
ax.set(xlabel='Time in usec', ylabel='Algorithm')
plt.tight_layout()
savefig(__file__)
plt.show()
