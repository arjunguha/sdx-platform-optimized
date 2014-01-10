#############################################
# Plot Pfx_2_participant                    #
# author: Arpit Gupta (glex.qsd@gmail.com)  #
#############################################
import os, sys,json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import cumfreq
#import matplotlib.pyplot as plt
import pylab as pl
import numpy as np
#import statsmodels.api as sm


loc=1
pfx_2_part=json.load(open('amsix-pfx_2_part.dat', 'r'))
a=pfx_2_part.values()
N=len(a)
print "data: ",N
if sum(a) != 0.0:
    counts, bin_edges = np.histogram(a,bins=range(1,max(a)+1),normed=True)
    print "counts: ",counts
    print "bin_edges: ",bin_edges
fig = plt.figure(figsize=(12,12))
ax = fig.add_subplot(1,1,1)
color_n=['g','m','c','r','b','k','w']
p1=pl.plot(bin_edges[:len(bin_edges)-1],map(lambda x:float(x)*100,counts),color=color_n[0], linewidth=5.0)
for tick in ax.xaxis.get_major_ticks():
    tick.label.set_fontsize(24)
for tick in ax.yaxis.get_major_ticks():
    tick.label.set_fontsize(24)
#pl.legend((p),select_ixp,'lower right',prop={'size':32})
pl.xlabel('#Participants advertising a prefix',fontsize=32)
pl.ylabel('%',fontsize=32)
pl.xlim(1,15)
pl.ylim(0.1,30)
ax.grid(True)
plot_name='pfx_2_part.eps'
plot_name_png='pfx_2_part.png'
pl.savefig(plot_name)
pl.savefig(plot_name_png)

