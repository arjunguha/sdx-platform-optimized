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
    dname=option+"BM.dat"
    if option=='compose':
        print "plotting "+str(option)+" result"
        dname="composeBM_matapan.dat"
        data=json.load(open(dname, 'r'))
        params=['space','time']
        xlab=[]
        for param in params:
            print "plotting for the param: ",param
            for k,v in data[param].iteritems():
                print k
                tmp_median=[]
                tmp_stddev=[]
                print v.keys()
                tmp={}
                for hdr in v:
                    tmp[int(hdr)]=v[hdr]
                v=tmp              
                v.keys().sort()
                xlab=v.keys()
                print v.keys()
                for hdr in sorted(v.iterkeys()):
                    print hdr,v[hdr]
                    total, average, median, standard_deviation, minimum, maximum, confidence=stats(v[hdr])
                    print median,standard_deviation
                    median=average
                    tmp_median.append(median)
                    tmp_stddev.append(standard_deviation)
                print "median: ",tmp_median
                data[param][k]['median']=tmp_median
                data[param][k]['stddev']=tmp_stddev
                
            fig = plt.figure(figsize=(12,12))
            ax = fig.add_subplot(1,1,1)
            color_n=['g','m','c','r','b','k','w']
            markers=['^','o','H','*']
            p1=[]
            i=0
            leg=[]
            
            for k in data[param].keys():
                leg.append(k)
                a=data[param][k]['median']
                v=data[param][k]
                err=data[param][k]['stddev']
                p1.append([])
                print sorted(v.iterkeys())
                xlab.sort()
                print "xlab: ",xlab
                p1[i]=pl.errorbar(xlab,a,yerr=err,markerfacecolor=color_n[i],
                              color='k', markersize=20,ecolor='k',marker=markers[i],
                              label=k,linewidth=4.0)
                i+=1
            p=[]
            i=0
            for k in data[param].keys():
                p.append(p1[i][0])
                i+=1
                
            for tick in ax.xaxis.get_major_ticks():
                tick.label.set_fontsize(24)
            for tick in ax.yaxis.get_major_ticks():
                tick.label.set_fontsize(24)
                
            pl.legend((p),leg,'upper left',prop={'size':32})
            pl.xlabel('# Participants',fontsize=32)
            if param=='space':
                pl.ylabel('# Flow Rules',fontsize=32)
            elif param=='time':
                pl.ylabel('Compilation Time (seconds)',fontsize=32)
                pl.xlim(15,165)
                pl.ylim(-10,500)
                
            ax.grid(True)
            
            plot_name=option+'_'+param+'.eps'
            plot_name_png=option+'_'+param+'.png'
            pl.savefig(plot_name)
            pl.savefig(plot_name_png)
    
    elif option=='predicate':
        print "plotting "+str(option)+" result"
        data=json.load(open(dname, 'r'))
        params=['space','time']
        for param in params:
            print "plotting for the param: ",param
            for k,v in data[param].iteritems():
                print k
                tmp_median=[]
                tmp_stddev=[]
                for hdr in v:
                    total, average, median, standard_deviation, minimum, maximum, confidence=stats(v[hdr])
                    print median,standard_deviation
                    tmp_median.append(median)
                    tmp_stddev.append(standard_deviation)
                print "median: ",tmp_median
                data[param][k]['median']=tmp_median
                data[param][k]['stddev']=tmp_stddev
                
            fig = plt.figure(figsize=(12,12))
            ax = fig.add_subplot(1,1,1)
            color_n=['g','m','c','r','b','k','w']
            p1=[]
            i=0
            leg=[]
            
            for k in data[param].keys():
                leg.append(k)
                a=data[param][k]['median']
                err=data[param][k]['stddev']
                p1.append([])
                p1[i]=pl.errorbar(range(1,len(a)+1),a,yerr=err,markerfacecolor=color_n[i],
                              marker='o',label=k,linewidth=5.0)
                i+=1
            p=[]
            i=0
            for k in data[param].keys():
                p.append(p1[i][0])
                i+=1
                
            for tick in ax.xaxis.get_major_ticks():
                tick.label.set_fontsize(24)
            for tick in ax.yaxis.get_major_ticks():
                tick.label.set_fontsize(24)
                
            pl.legend((p),leg,'lower right',prop={'size':32})
            pl.xlabel('# Header Fields',fontsize=32)
            if param=='space':
                pl.ylabel('# Flow Rules',fontsize=32)
            elif param=='time':
                pl.ylabel('Compilation Time (seconds)',fontsize=32)
                
            ax.grid(True)
            #pl.xlim(0.1,0.1)
            #pl.ylim((0.1,ax.get_ylim()))
            plot_name=option+'_'+param+'.eps'
            plot_name_png=option+'_'+param+'.png'
            pl.savefig(plot_name)
            pl.savefig(plot_name_png)
    
    if option=='pgroup':
        print "plotting "+str(option)+" result"
        #dname="composeBM_matapan.dat"
        data=json.load(open(dname, 'r'))
        params=['space','time']
        xlab=[]
        for param in params:
            print "plotting for the param: ",param
            for k,v in data[param].iteritems():
                print k
                tmp_median=[]
                tmp_stddev=[]
                print v.keys()
                tmp={}
                for hdr in v:
                    tmp[int(hdr)]=v[hdr]
                v=tmp              
                v.keys().sort()
                xlab=v.keys()
                print v.keys()
                for hdr in sorted(v.iterkeys()):
                    print hdr,v[hdr]
                    total, average, median, standard_deviation, minimum, maximum, confidence=stats(v[hdr])
                    print median,standard_deviation
                    #median=average
                    tmp_median.append(median)
                    tmp_stddev.append(standard_deviation)
                print "median: ",tmp_median
                data[param][k]['median']=tmp_median
                data[param][k]['stddev']=tmp_stddev
                
            fig = plt.figure(figsize=(12,12))
            ax = fig.add_subplot(1,1,1)
            color_n=['g','m','c','r','b','k','w']
            markers=['^','o','H','*']
            p1=[]
            i=0
            leg=[]
            
            for k in data[param].keys():
                leg.append(k)
                a=data[param][k]['median']
                v=data[param][k]
                err=data[param][k]['stddev']
                p1.append([])
                print sorted(v.iterkeys())
                xlab.sort()
                print "xlab: ",xlab
                p1[i]=pl.errorbar(xlab,a,yerr=err,markerfacecolor=color_n[i],
                              color='k', markersize=20,ecolor='k',marker=markers[i],
                              label=k,linewidth=4.0)
                i+=1
            p=[]
            i=0
            for k in data[param].keys():
                p.append(p1[i][0])
                i+=1
                
            for tick in ax.xaxis.get_major_ticks():
                tick.label.set_fontsize(24)
            for tick in ax.yaxis.get_major_ticks():
                tick.label.set_fontsize(24)
                
            pl.legend((p),leg,'upper left',prop={'size':32})
            pl.xlabel('# Prefix Groups',fontsize=32)
            if param=='space':
                pl.ylabel('# Flow Rules',fontsize=32)
            elif param=='time':
                pl.ylabel('Compilation Time (seconds)',fontsize=32)
                pl.xlim(15,105)
                #pl.ylim(-10,500)
                
            ax.grid(True)
            
            plot_name=option+'_'+param+'.eps'
            plot_name_png=option+'_'+param+'.png'
            pl.savefig(plot_name)
            pl.savefig(plot_name_png)
            
                

if __name__ == '__main__':
    main(sys.argv[1]) 