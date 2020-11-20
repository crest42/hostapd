from plot import *
x = 'clock'

new_df = pd.concat([df_total, df_eap]).sort_index()

tidy = new_df[new_df['sec_level'] == 3].groupby(['algo','type','run']).last().reset_index().sort_values(x)[['algo',x,'type']]
ax = sns.boxplot(data=tidy, y='algo', x=x, hue='type')
ax.set(xlabel='CPU Cycles', ylabel='Algorithm')
plt.tight_layout()
#savefig(__file__)

plt.show()
