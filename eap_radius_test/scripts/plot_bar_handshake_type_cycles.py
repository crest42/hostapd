from plot import *
x = 'clock_abs'
data=msg_cb[msg_cb['sec_level'] == 3].sort_values(x)
data = data[data['handshake_type_string'].isin(['client hello', 'server hello', 'finished'])]
sns.boxplot(data=data, y='groups', x=x, hue='handshake_type_string')
plt.show()
