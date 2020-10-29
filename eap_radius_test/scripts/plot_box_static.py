from plot import *

msg_cb = add_sec_level(msg_cb,'algo')
msg_cb_static = add_sec_level(pd.read_pickle('./pkl/msg_cb_static_zero_overhead.pkl'),'algo')

msg_cb_static = msg_cb_static[msg_cb_static['sec_level'] == 3]
msg_cb_static = msg_cb_static[msg_cb_static['hybrid'] == False]
msg_cb_static = msg_cb_static[msg_cb_static['algo'] != 'P-384']
msg_cb = msg_cb[msg_cb['sec_level'] == 3]
msg_cb = msg_cb[msg_cb['hybrid'] == False]
msg_cb = msg_cb[msg_cb['algo'] != 'P-384']

msg_cb_last = msg_cb[['rnd', 'algo', 'time_abs', 'clock_abs',  'clock']].groupby('rnd').last()
msg_cb_static_last = msg_cb_static[['rnd', 'algo', 'time_abs', 'clock_abs', 'clock']].groupby('rnd').last()
msg_cb_last['static'] = False
msg_cb_static_last['static'] = True
plot_df = pd.concat([msg_cb_static_last, msg_cb_last])


order = plot_df.groupby(['algo']).mean().reset_index().sort_values('clock_abs')['algo']

sns.boxplot(data=plot_df, y='algo', x='clock_abs', hue='static' , order = order)
#plt.show()
plt.tight_layout()
savefig(__file__)
res = ttest(msg_cb_static_last, msg_cb_last, 'clock_abs')
res = {k: v for k, v in sorted(res.items(), key=lambda item: item[1].pvalue)}

