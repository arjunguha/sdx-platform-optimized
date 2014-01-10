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
pfx_2_part=json.load(open('amsix-part_2_pfx.dat', 'r'))
a=pfx_2_part.values()
a.sort(reverse=True)
print a
N=len(a)
print "data: ",N
print "median: ",np.median(a)
print "mean: ",np.mean(a)

fig = plt.figure(figsize=(12,12))
ax = fig.add_subplot(1,1,1)
color_n=['g','m','c','r','b','k','w']
p1=pl.plot(range(1,N+1),map(lambda x: float(x)/1000,a),color=color_n[0], linewidth=5.0)
for tick in ax.xaxis.get_major_ticks():
    tick.label.set_fontsize(24)
for tick in ax.yaxis.get_major_ticks():
    tick.label.set_fontsize(24)
#pl.legend((p),select_ixp,'lower right',prop={'size':32})
pl.xlabel('Participants',fontsize=32)
pl.ylabel('#Prefixes Announced (K)',fontsize=32)

ax.grid(True)
plot_name='part_2_pfx.eps'
plot_name_png='part_2_pfx.png'
pl.savefig(plot_name)
pl.savefig(plot_name_png)

