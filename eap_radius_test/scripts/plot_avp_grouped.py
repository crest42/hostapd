from plot import *

merge = merge[merge['hybrid'] == False]
merge = merge[merge['algo'] != 'P-384']
tmp = cap_df[['algo', 'avp_count', 'rad_avp_t', 'rad_avp_len', 'rad_code']].groupby(['algo', 'rad_code', 'rad_avp_t']).sum().reset_index().sort_values('rad_avp_len')
tmp = tmp[tmp['rad_avp_t']  != '79']
tmp['rad_avp_t_long'] = None
tmp['rad_code_long'] = None
tmp['mandatory'] = False

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

_m = ['1', '61', '4', '80', '24']

for k in _m:
    tmp.loc[tmp['rad_avp_t'] == k, 'mandatory'] = True

for k in m:
    tmp.loc[tmp['rad_avp_t'] == k, 'rad_avp_t_long'] = m[k]

for k in m_c:
    tmp.loc[tmp['rad_code'] == k, 'rad_code_long'] = m_c[k]

ax = sns.boxplot(data=tmp.groupby(['algo', 'mandatory']).sum().reset_index(), x='mandatory', y='rad_avp_len')
ax.set(xlabel='Mandatory', ylabel='Sum AVP Bytes')
savefig(__file__)

#plt.show()
