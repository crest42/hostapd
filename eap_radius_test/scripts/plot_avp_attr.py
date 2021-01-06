from plot import *

#tmp = cap_df[['algo', 'avp_count', 'rad_avp_t', 'rad_avp_len', 'rad_code']].groupby(['algo', 'rad_code', 'rad_avp_t']).sum().reset_index().sort_values('rad_avp_len')
tmp = cap_df[['algo', 'run', 'frame_count', 'avp_count', 'rad_avp_t', 'rad_avp_len', 'rad_code']].groupby(['algo', 'run', 'frame_count', 'avp_count']).first().reset_index().groupby(['algo', 'run', 'rad_code', 'rad_avp_t']).sum().reset_index().sort_values('rad_avp_len')
tmp = tmp[tmp['rad_avp_t']  != '79']
tmp['rad_avp_t_long'] = None
tmp['rad_code_long'] = None

m = {'1': 'User-Name',
       '4': 'NAS-IP-Address',
       '6': 'Service Type',
       '12': 'Framed-MTU',
       '24': 'State',
       '26': 'Vendor Specific',
       '31': 'Calling-Station-Id',
       '61': 'NAS-Port-Type',
       '77': 'Connect-Info',
       '80': 'Message Authenticator'
}

m_c = {'1': 'Access-Request',
        '2': 'Access-Accept',
        '11': 'Access-Challenge'}

for k in m:
    tmp.loc[tmp['rad_avp_t'] == k, 'rad_avp_t_long'] = m[k]

for k in m_c:
    tmp.loc[tmp['rad_code'] == k, 'rad_code_long'] = m_c[k]

tmp = tmp[tmp['rad_code_long'] != 'Access-Accept']
tmp = tmp.rename({'rad_code': 'Radius Type', 'rad_avp_len': 'Bytes', 'rad_avp_t_long': 'AVP Type'}, axis=1)

sns.boxplot(data=tmp.sort_values(['Radius Type','Bytes']), x='Radius Type', y='Bytes', hue='AVP Type')
savefig(__file__)

#plt.show()
