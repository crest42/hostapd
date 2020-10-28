from plot import *

full = pd.read_pickle('./pkl/cap_df_0ms.pkl')
sparse = pd.read_pickle('./pkl/cap_df_sparse.pkl')

full = full.groupby(['algo','run','frame_count','avp_count']).first().reset_index()
sparse = sparse.groupby(['algo','run','frame_count','avp_count']).first().reset_index()








sparse = sparse.groupby(['algo','run','frame_count','avp_count']).first().reset_index().groupby(['algo','run', 'rad_avp_t']).sum().reset_index()
full = full.groupby(['algo','run','frame_count','avp_count']).first().reset_index().groupby(['algo','run', 'rad_avp_t']).sum().reset_index()
sparse = sparse[sparse['rad_avp_t'] != '79']
full = full[full['rad_avp_t'] != '79']
full['type'] = 'Full'
sparse['type'] = 'Sparse'

final = pd.concat([full[['algo','run','rad_avp_t','rad_avp_len','type']], sparse[['algo','run','rad_avp_t','rad_avp_len','type']]])

sns.boxplot(data=final.groupby(['algo','run','type']).sum().reset_index(), x='type', y='rad_avp_len')

savefig(__file__)

#plt.show()
