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

top=20
pg_stats=json.load(open('amsix-pg_stats.dat', 'r'))
#print pg_stats
total_announced=[]
announced2groups={}
for nh in pg_stats:
    total_announced.append(pg_stats[nh][0])
    announced2groups[pg_stats[nh][0]]=pg_stats[nh][1]
total_announced.sort(reverse=True)
#print total_announced
a=[]
b=[]
for i in range(top):
    a.append(total_announced[i])
    b.append(announced2groups[total_announced[i]])
#print a,b
#data=[a,b]
fig = plt.figure(figsize=(12,12))
ax = fig.add_subplot(1,1,1)
color_n=['g','m','c','r','b','k','w']

p1=pl.plot(range(1,top+1),map(lambda x:int(float(x)/1000),a),color=color_n[0], linewidth=5.0)
p2=pl.plot(range(1,top+1),map(lambda x:int(float(x)/1000),b),color=color_n[1], linewidth=5.0)
for tick in ax.xaxis.get_major_ticks():
    tick.label.set_fontsize(24)
for tick in ax.yaxis.get_major_ticks():
    tick.label.set_fontsize(24)
p=[p1,p2]
#lgnd=['# Prefixes Announced','# Prefix Groups']

#pl.legend((p),lgnd,'upper right',prop={'size':32})    
pl.xlabel('Participants',fontsize=32)
pl.ylabel('# Prefixes (K)',fontsize=32)

ax.grid(True)
plot_name='fib_explosion.eps'
plot_name_png='fib_explosion.png'
pl.savefig(plot_name)
pl.savefig(plot_name_png)

    


    

"""
nh,total,fraction,a=pg_stats.values()[0]
a.sort(reverse=True)
N=len(a)
print "data: ",N

print "median: ",np.median(a)
print "mean: ",np.mean(a)

fig = plt.figure(figsize=(12,12))
ax = fig.add_subplot(1,1,1)
color_n=['g','m','c','r','b','k','w']

p1=pl.plot(range(1,N+1),a,color=color_n[0], linewidth=5.0)
for tick in ax.xaxis.get_major_ticks():
    tick.label.set_fontsize(24)
for tick in ax.yaxis.get_major_ticks():
    tick.label.set_fontsize(24)
    
pl.xlabel('Prefix Groups',fontsize=32)
pl.ylabel('# Prefixes',fontsize=32)

ax.grid(True)
plot_name='pg_distr.eps'
plot_name_png='pg_distr.png'
pl.savefig(plot_name)
pl.savefig(plot_name_png)
"""