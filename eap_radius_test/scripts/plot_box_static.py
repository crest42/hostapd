from plot import *

msg_cb = add_sec_level(pd.read_pickle('./pkl/msg_cb_sparse.pkl'),'algo')
msg_cb_static = add_sec_level(pd.read_pickle('./pkl/msg_cb_static.pkl'),'algo')

msg_cb_static = msg_cb_static[msg_cb_static['sec_level'] == 3]
msg_cb = msg_cb[msg_cb['sec_level'] == 3]

msg_cb_last = msg_cb[['rnd', 'algo', 'time_abs', 'clock_abs',  'clock']].groupby('rnd').last()
msg_cb_static_last = msg_cb_static[['rnd', 'algo', 'time_abs', 'clock_abs', 'clock']].groupby('rnd').last()
msg_cb_last['static'] = False
msg_cb_static_last['static'] = True
plot_df = pd.concat([msg_cb_static_last, msg_cb_last])


order = plot_df.groupby(['algo']).mean().reset_index().sort_values('clock')['algo']

sns.boxplot(data=plot_df, y='algo', x='clock', hue='static' , order = order)
#plt.show()
plt.tight_layout()
savefig(__file__)
