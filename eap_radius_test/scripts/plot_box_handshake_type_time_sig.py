from plot_sig import *
palette = sns.color_palette("Paired")

sns.set(font_scale=1.3, context='paper', palette=palette)
sns.set_style(sns.axes_style("ticks"),
              {'axes.grid': True})
(msg_cb, info_cb, df_total, df_eap, cap_df) = get_inst_cb()
print("Data loaded")
x = 'time_abs'
add_sec_level(msg_cb,'algo')
data=msg_cb[msg_cb['sec_level'] == 3]
data = data[data['hybrid'] == False]
data = data[data['handshake_type_string'].isin(['client hello', 'server hello', 'finished'])]
data = data.groupby(['algo','run','handshake_type_string']).last().reset_index().sort_values(['algo','clock'])
order = data[data['handshake_type_string'] == 'finished'].groupby(['algo']).mean().reset_index().sort_values('time_abs')['algo']
data = data.rename({'handshake_type_string': 'handshake_type'},axis=1)
g = sns.FacetGrid(data, col="handshake_type",  sharex=False)
g.map_dataframe(sns.boxplot, y='algo',order=order, x='clock')

for f in g.axes.flat:
    f.set(xlabel='', ylabel='',title=f.get_title()[17:])
g.set_axis_labels("CPU Cycles", "")
#ax = sns.barplot(data=data, y='algo', x=x, hue='handshake_type_string', order=order)
#ax.set(xlabel='Time in usec', ylabel='Algorithm')
#ax.set_xscale("log")
plt.tight_layout()

savefig(__file__)

#plt.show()
