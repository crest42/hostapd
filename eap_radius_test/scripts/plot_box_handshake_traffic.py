from plot import *
x = 'sum_len'
sns.barplot(data=msg_cb[msg_cb['sec_level'] == 3].groupby('rnd').last().sort_values(x), y='groups', x=x)
plt.show()
