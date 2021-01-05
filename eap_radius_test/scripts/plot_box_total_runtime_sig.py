from plot_sig import *
x = 'clock'
(msg_cb, info_cb, df_total, df_eap, cap_df) = get_inst_cb()

new_df = pd.concat([add_sec_level(df_total,'algo'), add_sec_level(df_eap,'algo')]).sort_index()
new_df = new_df[new_df['hybrid'] == False]
tidy = new_df[new_df['sec_level'].isin([3,5])].groupby(['algo','type','run']).last().reset_index().sort_values(x)[['algo',x,'type']]
order = tidy.groupby('algo').median().sort_values(x).index
ax = sns.boxplot(data=tidy, y='algo', x=x, hue='type', order = order)
ax.set(xlabel='CPU Cycles', ylabel='Algorithm')
plt.tight_layout()
savefig(__file__)

#plt.show()
