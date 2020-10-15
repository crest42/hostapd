from plot import *
x = 'clock'
from sklearn.preprocessing import MinMaxScaler, RobustScaler
from sklearn import datasets, linear_model
new_df = df_total

tidy = new_df[new_df['sec_level'] == 3].groupby(['algo','type','run']).last().reset_index().sort_values(x)[['algo',x,'type']]

scaler = MinMaxScaler()

#ax = sns.boxplot(data=tidy, y='algo', x=x, hue='type')
#ax.set(xlabel='CPU Cycles', ylabel='Algorithm')
#plt.tight_layout()

robocop = [
        ['bike1l3fo','BIKE-1-3', 751792, 753165, 756135, 114548, 115245, 115988, 3533895, 3544650, 3563393, 52732//8, 49642//8, 49642//8, -1],
        ['frodo976aes','FrodoKEM-976-AES', 9325508, 9332527, 9342787, 3030097, 3033135, 3045172, 2981970, 2985502, 2996797, 31296, 15632, 15744, 24],
        ['frodo976shake','FrodoKEM-976-SHAKE', 15867922, 15887925, 15915150, 9271755, 9276953, 9287617, 9220680, 9229140, 9237847, 31296, 15632, 15744, 24],
        ['hqc192_1','hqc-192-1', 439875, 443970, 451530, 889515, 900203, 905108, 1623285, 1634377, 1641622, 5539, 5499, 10981, 64],
        ['hqc192_2','hqc-192-2', 466763, 475920, 483165, 951885, 960885, 973530, 1671232, 1693957, 1706827, 5924, 5884, 11749, 64],
        ['kyber768','Kyber768', 50895, 51007, 51187, 69255, 69300, 69390, 61132, 61155, 61223, 2400, 1184, 1088, 32],
        ['kyber90s768','Kyber768-90s', 15007, 15120, 15323, 22207, 22230, 22253, 23513, 23558, 23603, 2400, 1184, 1088, 32],
        ['ntru_hps2048677','ntruhps2048677', 324292, 324720, 325215, 32895, 33075, 33727, 58095, 58140, 59153, 1234, 930, 930, 32],
        ['ntru_hrss701','ntruhrss701', 348750, 349155, 351945, 29137, 29205, 29970, 70943, 71010, 71055, 1450, 1138, 1138, 32],
        ['saber','saber2-KEM', 70357, 70380, 70470, 89888, 89933, 90000, 90337, 90382, 90405, 2304, 992, 1088, -1],
        ['sikep610','SIKEp610', 160401*1000, 160401*1000, 160401*1000, 294628*1000, 294628*1000, 294628*1000, 296577*1000, 296577*1000, 296577*1000, 524, 462, 486, 24],
]

robo_df = pd.DataFrame(robocop, columns=['name', 'name_robo', 'gen-25th', 'gen-50th', 'gen-75th',
           'enc-25th', 'enc-50th', 'enc-75th',
           'dec-25th', 'dec-50th', 'dec-75th',
           'sk', 'Public Key Size', 'ct', 'sesk'])
new_df = new_df[new_df['algo'].isin(robo_df['name'])].groupby('algo').mean().sort_values('algo').reset_index()[['algo','clock']]

robo_df['total'] = robo_df['gen-50th'] +  robo_df['enc-50th']
robo_df = robo_df[['name','total']]
robo_df['hue'] = 'robo'
new_df['hue'] = 'new'
new_df['clock'] =  np.log(new_df['clock'])
robo_df['total'] = np.log(robo_df['total'])
new_df['clock'] = scaler.fit_transform(np.array(new_df['clock']).reshape(-1,1))
robo_df['total'] = scaler.fit_transform(np.array(robo_df['total']).reshape(-1,1))
#robo_df = robo_df.rename(columns={'name': 'algo', 'total': 'clock'})
#savefig(__file__)
#plot_df = pd.concat([new_df, robo_df])
#plot_df = plot_df.sort_values('clock')
plot_df = new_df.sort_values('algo')
plot_df['total'] = robo_df.sort_values('name')['total']

ax =sns.scatterplot(data=plot_df, y='clock', x='total', hue='algo', style='algo')
regr = linear_model.LinearRegression()
regr.fit(np.array(plot_df['clock']).reshape(-1,1), np.array(plot_df['total']).reshape(-1,1))
uni = np.linspace(0,1,100)
reg_line = pd.DataFrame([[uni[i], regr.coef_[0][0]*uni[i]] for i,x in enumerate(uni)], columns=['x','y'])


ax =sns.lineplot(data=reg_line, y='y', x='x')
ax.set(xlabel='Cycles hostpad', ylabel='Cycles Robocop')
ax.legend(loc='best')


savefig(__file__)
#ax.set(xscale="log", yscale="log")
#g = sns.FacetGrid(plot_df, col='hue')
#g.map(sns.barplot, 'clock','algo') 
#plt.show()
