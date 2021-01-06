from plot_sig import *

merge = get_cap_df()
add_sec_level(merge, 'algo')
merge = merge[merge['hybrid'] == False]
cap_size_df = merge[['algo','run','frame_nr','frame_len', 'rad_len', 'rad_avp_len', 'eap.len', 'tls_record_length']].groupby(['algo','run','frame_nr']).agg({'frame_len': 'first', 'rad_len': 'first', 'rad_avp_len': 'sum', 'eap.len': 'sum', 'tls_record_length': 'sum'}).reset_index().groupby(['algo','run']).sum().reset_index()[['algo','run','frame_len', 'rad_len', 'rad_avp_len', 'eap.len', 'tls_record_length']].melt(id_vars=['algo','run'])
order = cap_size_df[cap_size_df['variable'] == 'frame_len'].groupby('algo').mean().reset_index().sort_values('value')['algo']


cap_size_df = cap_size_df.rename({'variable': 'Protocol Type', 'algo': 'Algorithm', 'value': 'Bytes'}, axis=1)
cap_size_df.loc[(cap_size_df['Protocol Type'] == 'tls_record_length'),'Protocol Type'] = 'TLS Records'
cap_size_df.loc[(cap_size_df['Protocol Type'] == 'eap.len'),'Protocol Type'] = 'EAP'
cap_size_df.loc[(cap_size_df['Protocol Type'] == 'rad_avp_len'),'Protocol Type'] = 'Radius AVP'
cap_size_df.loc[(cap_size_df['Protocol Type'] == 'rad_len'),'Protocol Type'] = 'Radius'
cap_size_df.loc[(cap_size_df['Protocol Type'] == 'frame_len'),'Protocol Type'] = 'Ethernet'


sns.barplot(data=cap_size_df.sort_values('Bytes'), y = 'Algorithm', x = 'Bytes', hue='Protocol Type', order=order)
plt.tight_layout()
savefig(__file__)
#plt.show()

