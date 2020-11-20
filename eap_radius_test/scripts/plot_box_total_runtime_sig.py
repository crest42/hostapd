from plot_sig import *
x = 'clock'

new_df = pd.concat([add_sec_level(df_total,'algo'), add_sec_level(df_eap,'algo')]).sort_index()
new_df = new_df[new_df['hybrid'] == False]
tidy = new_df[new_df['sec_level'].isin([3,5])].groupby(['algo','type','run']).last().reset_index().sort_values(x)[['algo',x,'type']]
ax = sns.boxplot(data=tidy, y='algo', x=x, hue='type')
ax.set(xlabel='CPU Cycles', ylabel='Algorithm')
plt.tight_layout()
savefig(__file__)

#plt.show()
