from plot import *
y = 'time_abs'
x = 'sum_len'
sns.scatterplot(data=msg_cb[msg_cb['sec_level'] == 3], y=y, x=x,hue='groups')
plt.show()
