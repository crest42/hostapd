from plot import *
x = 'rstime'
sns.boxplot(data=msg_cb[msg_cb['sec_level'] == 3].groupby('rnd').last().sort_values(x), y='groups', x=x)
plt.show()
