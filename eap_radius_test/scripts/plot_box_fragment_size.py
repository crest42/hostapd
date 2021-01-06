from plot import *


merge = pd.read_pickle('./pkl/sig/cap_df_fragment_size.pkl')
merge['mtu'] = merge['algo'].str.split('_', expand=True)[1]
merge['mtu'] = merge['mtu'].astype(int)
cap_size_df = merge[['algo','run','frame_nr','frame_len', 'mtu']].groupby(['algo','run','frame_nr']).agg({'mtu': 'first', 'frame_len': 'first'}).groupby(['algo','run','mtu']).sum().reset_index()

sns.boxplot(data=cap_size_df.rename({'mtu': 'MTU Size in Bytes', 'frame_len': 'Sum Ethernet Frame Bytes'},axis=1), x = 'MTU Size in Bytes', y = 'Sum Ethernet Frame Bytes',color=colors[0])
plt.tight_layout()
savefig(__file__)
#plt.show()

