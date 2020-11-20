from plot_sig import *
y = 'time_abs'
x = 'sum_len'
add_sec_level(msg_cb,'algo')
sns.scatterplot(data=msg_cb[msg_cb['sec_level'] == 3], y=y, x=x,hue='algo')
plt.show()
