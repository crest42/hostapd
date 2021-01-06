from plot import *
x = 'clock'

new_df = pd.concat([df_total, df_eap]).sort_index()
tidy = new_df[new_df['sec_level'] == 3].groupby(['algo','type','run']).last().reset_index().sort_values(x)[['algo',x,'type']]
order =  tidy.groupby('algo').median().sort_values('clock').index
tidy = tidy.rename({'type': 'Runtime'}, axis=1)
tidy.loc[(tidy.Runtime == 'time_total'),'Runtime'] = 'Total'
tidy.loc[(tidy.Runtime == 'time_eap'),'Runtime'] = 'EAP'
ax = sns.boxplot(data=tidy, y='algo', x=x, hue='Runtime', order=order)
ax.set(xlabel='CPU Cycles', ylabel='Algorithm')
plt.tight_layout()
savefig(__file__)

#plt.show()
