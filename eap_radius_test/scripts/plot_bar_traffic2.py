from plot import *

merge = merge[merge['hybrid'] == False]
cap_size_df = merge.groupby(['algo','run']).sum().reset_index()[['algo','run','frame_len', 'rad_len', 'rad_avp_len', 'eap.len', 'tls.record.length']].melt(id_vars=['algo','run'])
order = cap_size_df[cap_size_df['variable'] == 'frame_len'].groupby('algo').mean().reset_index().sort_values('value')['algo']

cap_size_df = cap_size_df.rename({'variable': 'Protocol Type'}, axis=1)
cap_size_df.loc[(cap_size_df['Protocol Type'] == 'tls.record.length'),'Protocol Type'] = 'TLS Records'
cap_size_df.loc[(cap_size_df['Protocol Type'] == 'eap.len'),'Protocol Type'] = 'EAP'
cap_size_df.loc[(cap_size_df['Protocol Type'] == 'rad_avp_len'),'Protocol Type'] = 'Radius AVP'
cap_size_df.loc[(cap_size_df['Protocol Type'] == 'rad_len'),'Protocol Type'] = 'Radius'
cap_size_df.loc[(cap_size_df['Protocol Type'] == 'frame_len'),'Protocol Type'] = 'Ethernet'

ax = sns.barplot(data=cap_size_df.sort_values('value'), y = 'algo', x = 'value', hue='Protocol Type', order=order)
ax.set(xlabel='Sum of Traffic in Bytes', ylabel='Algorithm')
plt.tight_layout()
savefig(__file__)
#plt.show()

