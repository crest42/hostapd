from plot import *
from scipy.stats import ttest_ind

algos = []
pvalues = []
mean_np = []
mean_p = []

def do_ttest(ttest):
    mean = 0
    l = set(ttest[ttest['hybrid'] == 'False']['algo'].values)
    for x in l:
        if x == 'P-384':
            continue
        a = np.array(ttest[ttest['algo'] == x]['frame_len'].values)
        b = np.array(ttest[ttest['algo'] == f'p384_{x}']['frame_len'].values)
        print()
        print(x)
        print(a)
        print(np.mean(a))
        print(b)
        print(np.mean(b))
        print(np.abs(np.mean(a) - np.mean(b)))
        test = ttest_ind(a,b,equal_var=True)
        print(float(test.pvalue))
        algos.append(x)
        pvalues.append(test.pvalue)
        mean_np.append(np.mean(a))
        mean_p.append(np.mean(b))
        mean += test.pvalue
    print("Mean p-value:")
    print(float(mean)/len(l))

merge = merge[merge['sec_level'] == 3]
#merge = merge[merge['algo'] != 'P-384']
df = merge.groupby(['algo','run','pq_algo', 'classical_algo']).sum().reset_index()
hybrid = merge.hybrid > 0
non_hybrid = merge.hybrid == 0
merge.loc[non_hybrid, 'hybrid'] = "False"
merge.loc[hybrid, 'hybrid'] = "True"
ttest = merge.groupby(['algo','run']).agg({'pq_algo': 'first', 'frame_len': 'sum', 'hybrid': 'first'}).reset_index()
do_ttest(ttest)
order = merge[merge['hybrid'] == 'False'].groupby(['algo','run']).sum().groupby('algo').mean().sort_values('frame_len')
sns.barplot(data=merge.groupby(['algo','run']).agg({'pq_algo': 'first', 'frame_len': 'sum', 'hybrid': 'first'}).sort_values('frame_len'), y='pq_algo', hue='hybrid', x='frame_len', ci=0, order = order.reset_index()['algo'])
plt.tight_layout()
savefig(__file__)
#plt.show()

