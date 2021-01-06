from plot import *

msg_cb = add_sec_level(pd.read_pickle('./pkl/kem/msg_cb_practical.pkl'),'algo')

msg_cb = msg_cb[['rnd', 'algo', 'run','time_abs', 'clock_abs',  'clock','sum_len']].groupby(['algo','run']).last().reset_index()
msg_cb['algo'] = msg_cb['algo'].replace({'falcon1024': 'PQ', 'p521_falcon1024': 'Hybrid', 'p521': 'ECDH', 'rsa4096': 'RSA'})
order = ['RSA', 'ECDH', 'PQ', 'Hybrid']
order = msg_cb.groupby('algo').median().sort_values('clock_abs').index.values
sns.scatterplot(data=msg_cb.rename({'sum_len': 'Sum Traffic in Bytes', 'clock_abs': 'CPU Cycles', 'algo': 'Type'}, axis=1), x='Sum Traffic in Bytes', y='CPU Cycles', hue='Type')
#plt.show()
plt.tight_layout()
savefig(__file__)

