#############################################
# author: Arpit Gupta (glex.qsd@gmail.com)  #
#############################################
"""
Generic data plotting script
"""

import os, sys, json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from netaddr import *
from scipy.stats import cumfreq
#import matplotlib.pyplot as plt
import pylab as pl
import numpy as np
from statistics import *

def main(option):
    if option=='predicate':
        print "plotting predicate BM result"
        data=json.load(open('predicateBM.dat', 'r'))
        for k,v in data['space'].iteritems():
            print k
            tmp_median=[]
            tmp_stddev=[]
            for hdr in v:
                total, average, median, standard_deviation, minimum, maximum, confidence=stats(v[hdr])
                #print median,standard_deviation
                tmp_median.append(median)
                tmp_stddev.append(standard_deviation)
            print "median: ",tmp_median
            data['space'][k]['median']=tmp_median
            data['space'][k]['stddev']=tmp_stddev
        fig = plt.figure(figsize=(12,12))
        ax = fig.add_subplot(1,1,1)
        color_n=['g','m','c','r','b','k','w']
        p1=[]
        i=0
        leg=[]
        
        for k in data['space'].keys():
            leg.append(k)
            a=data['space'][k]['median']
            err=data['space'][k]['stddev']
            p1.append([])
            p1[i]=pl.errorbar(range(1,len(a)+1),a,yerr=err,markerfacecolor='g',
                          marker='o',label=k,linewidth=5.0)
            i+=1
        p=[]
        i=0
        for k in data['space'].keys():
            p.append(p1[i][0])
            i+=1
            
        for tick in ax.xaxis.get_major_ticks():
            tick.label.set_fontsize(24)
        for tick in ax.yaxis.get_major_ticks():
            tick.label.set_fontsize(24)
            
        pl.legend((p),leg,'lower right',prop={'size':32})
        pl.xlabel('# Header Fields',fontsize=32)
        pl.ylabel('# Flow Rules',fontsize=32)
        ax.grid(True)
        #pl.xlim(0.1,0.1)
        #pl.ylim((0.1,ax.get_ylim()))
        plot_name='predicate_space.eps'
        plot_name_png='predicate_space.png'
        pl.savefig(plot_name)
        pl.savefig(plot_name_png)
         
            
                

if __name__ == '__main__':
    main(sys.argv[1]) 