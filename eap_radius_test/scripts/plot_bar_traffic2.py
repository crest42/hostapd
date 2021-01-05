from plot import *

merge = merge[merge['hybrid'] == False]
cap_size_df = merge.groupby(['algo','run']).sum().reset_index()[['algo','run','frame_len', 'rad_len', 'rad_avp_len', 'eap.len', 'tls.record.length']].melt(id_vars=['algo','run'])
order = cap_size_df[cap_size_df['variable'] == 'frame_len'].groupby('algo').mean().reset_index().sort_values('value')['algo']
ax = sns.barplot(data=cap_size_df.sort_values('value'), y = 'algo', x = 'value', hue='variable', order=order)
ax.set(xlabel='Sum of Traffic in Bytes', ylabel='Algorithm')
plt.tight_layout()
savefig(__file__)
#plt.show()

