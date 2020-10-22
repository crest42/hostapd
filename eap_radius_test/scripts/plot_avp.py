from plot import *

merge = merge[merge['hybrid'] == False]
merge = merge[merge['algo'] != 'P-384']
tmp = merge[['algo', 'run', 'rad_len', 'rad_avp_len', 'frame_len','eap.len', 'tls.record.length']].groupby(['algo', 'run']).sum().reset_index()
tmp['avp_wo_eap'] = tmp['rad_avp_len'] - tmp['eap.len']
tmp['frac'] = tmp['avp_wo_eap'] / tmp['frame_len']


tmp['TLS/Total'] = tmp['tls.record.length'] / tmp['frame_len']
tmp['EAP/AVP'] = tmp['eap.len'] / tmp['rad_avp_len']
tmp['AVP/Radius'] = tmp['rad_avp_len'] / tmp['rad_len']
tmp['TLS/EAP'] = tmp['tls.record.length'] / tmp['eap.len']

test = tmp[['algo','TLS/Total', 'TLS/EAP', 'EAP/AVP', 'AVP/Radius']].melt(id_vars=['algo'])
sns.boxplot(data=test, y='value', x='variable', order = ['TLS/Total','EAP/AVP', 'AVP/Radius', 'TLS/EAP'])
#plt.show()
savefig(__file__)
