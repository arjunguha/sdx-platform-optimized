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

def restructureData(data):
    tmp={}
    for k1 in data['#vnhs']:
        for k2 in data['#vnhs'][k1]:
            if k2 not in tmp:
                tmp[k2]={}
            tmp[k2][int(k1)]=data['#vnhs'][k1][k2]
    print tmp
    data['#vnhs']=tmp
    return data

def main(option):
    #dname='MDS_Fri24Jan2014051146.dat' 
    #dname='MDS_Fri24Jan2014060412.dat'
    #dname='mdsTrace_Sat25Jan2014032939.dat' 
    #dname='bgpUpdate_Sat25Jan2014101855.dat'
    #dname='bgpUpdate_Sat25Jan2014114145.dat'
    #dname='UPDATEDcompileTime_Sun26Jan2014194001.dat'
    dname='bgpUpdate_Tue28Jan2014061201.dat'
    dname='UPDATEDcompileTime_Tue28Jan2014063420.dat'
    
    if option=='initCompile':
        print "plotting "+str(option)+" result" 
        print "plotting "+str(option)+" result"
        #dname="composeBM_matapan.dat"
        data=json.load(open(dname, 'r'))
        #data=restructureData(data)
        params=['nrules','cTime','augmentTime','cacheSize']
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
                    tmp[float(hdr)]=v[hdr]
                v=tmp              
                v.keys().sort()
                xlab=v.keys()
                print v.keys()
                for hdr in sorted(v.iterkeys()):
                    print hdr,v[hdr]
                    #formating error hack
                    #v[hdr]=[v[hdr][0][0],v[hdr][1][0]]
                    print v[hdr]
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
            markers=['o','*','^','s','d','3','d','o','*','^','1','4']
            p1=[]
            i=0
            leg=data[param].keys()
            leg.sort(reverse=True)
            legnd=[]
            for k in leg:
                #leg.append(float(k))
                
                legnd.append('#Participants='+str(int(k))+'')
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
                #pl.text(xlab[int(float(len(xlab)/2))],20+a[int(float(len(a)/2))],'frac= '+str(k),fontsize=20,horizontalalignment='center')
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
            leg.sort() 
            pl.legend((p),legnd,'upper left',prop={'size':24})
            pl.xlabel('# Prefix Groups',fontsize=32)
            if param=='cacheSize':
                pl.ylabel('Bytes',fontsize=32)
                #pl.xlim(0,51)
                #ax.set_ylim(ymin=1)
            elif param=='cTime':
                pl.ylabel('Time (seconds)',fontsize=32)
                
            elif param=='augmentTime':
                pl.ylabel('Time (seconds)',fontsize=32)
                
            elif param=='nrules':
                pl.ylabel('# Flow Rules',fontsize=32)
                #pl.xlim(0,51)
                #ax.set_ylim(ymin=1)

                
            ax.grid(True)
            
            plot_name=option+'_'+param+'.eps'
            plot_name_png=option+'_'+param+'.png'
            pl.savefig(plot_name)
            pl.savefig(plot_name_png)
       
    
    elif option=='bgpUpdate':
        print "plotting "+str(option)+" result"
        #dname="composeBM_matapan.dat"
        data=json.load(open(dname, 'r'))
        #data=restructureData(data)
        params=['updateTime','deltaRules']
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
                    tmp[float(hdr)]=v[hdr]
                v=tmp              
                v.keys().sort()
                xlab=v.keys()
                print v.keys()
                for hdr in sorted(v.iterkeys()):
                    print hdr,v[hdr]
                    #formating error hack
                    #v[hdr]=[v[hdr][0][0],v[hdr][1][0]]
                    print v[hdr]
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
            markers=['o','*','^','s','d','3','d','o','*','^','1','4']
            p1=[]
            i=0
            leg=data[param].keys()
            leg.sort(reverse=True)
            legnd=[]
            for k in leg:
                #leg.append(float(k))
                
                legnd.append('#Participants='+str(int(k))+'')
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
                #pl.text(xlab[int(float(len(xlab)/2))],20+a[int(float(len(a)/2))],'frac= '+str(k),fontsize=20,horizontalalignment='center')
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
            leg.sort() 
            pl.legend((p),legnd,'upper left',prop={'size':24})
            pl.xlabel('Burst Size (BGP Updates)',fontsize=32)
            if param=='deltaRules':
                pl.ylabel('# Additional Rules',fontsize=32)
                pl.xlim(0,51)
                ax.set_ylim(ymin=1)
            elif param=='updateTime':
                pl.ylabel('Time (seconds)',fontsize=32)
                pl.xlim(0,51)
                ax.set_ylim(ymin=0)

                
            ax.grid(True)
            
            plot_name=option+'_'+param+'.eps'
            plot_name_png=option+'_'+param+'.png'
            pl.savefig(plot_name)
            pl.savefig(plot_name_png)
        
    elif option=='MDS':
        print "plotting "+str(option)+" result"
        #dname="composeBM_matapan.dat"
        data=json.load(open(dname, 'r'))
        #data=restructureData(data)
        params=['nvnhs','mdsTime','augmentTime']
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
                    tmp[float(hdr)]=v[hdr]
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
            markers=['o','*','^','s','d','3','d','o','*','^','1','4']
            p1=[]
            i=0
            leg=data[param].keys()
            leg.sort(reverse=True)
            legnd=[]
            for k in leg:
                #leg.append(float(k))
                
                #legnd.append('N= '+str(int(k)))
                legnd.append('#Participants='+str(int(k))+'')
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
                #pl.text(xlab[int(float(len(xlab)/2))],20+a[int(float(len(a)/2))],'frac= '+str(k),fontsize=20,horizontalalignment='center')
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
            leg.sort() 
            pl.legend((p),legnd,'upper left',prop={'size':24})
            pl.xlabel('# Prefixes',fontsize=32)
            if param=='nvnhs':
                pl.ylabel('# Prefix Groups',fontsize=32)
                pl.xlim(0,10000+100)
                ax.set_ylim(ymin=1)
            elif param=='mdsTime':
                pl.ylabel('Time(seconds)',fontsize=32)
                pl.xlim(0,10000+100)
                ax.set_ylim(ymin=1)
            elif param=='augmentTime':
                pl.ylabel('Time',fontsize=32)
                pl.xlim(0,10000+100)
                ax.set_ylim(ymin=1)
                #pl.ylim(-10,500)
                
            ax.grid(True)
            
            plot_name=option+'_'+param+'.eps'
            plot_name_png=option+'_'+param+'.png'
            pl.savefig(plot_name)
            pl.savefig(plot_name_png)
            
            
    elif option=='MDS-amsix':
        print "plotting "+str(option)+" result"
        #dname="composeBM_matapan.dat"
        data=json.load(open(dname, 'r'))
        #data=restructureData(data)
        params=['nvnhs','mdsTime']
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
                    tmp[float(hdr)]=v[hdr]
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
            markers=['o','*','^','s','d','3','d','o','*','^','1','4']
            p1=[]
            i=0
            leg=data[param].keys()
            tmp=[]
            for elem in leg:
                tmp.append(int(elem))
            leg=tmp
            leg.sort(reverse=True)
            legnd=[]
            for k in leg:
                #leg.append(float(k))
                
                legnd.append('#Participants='+str(int(k))+'')
                k=unicode(k)
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
                #pl.text(xlab[int(float(len(xlab)/2))],20+a[int(float(len(a)/2))],'frac= '+str(k),fontsize=20,horizontalalignment='center')
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
            leg.sort() 
            pl.legend((p),legnd,'upper left',prop={'size':24})
            pl.xlabel('# Prefixes',fontsize=32)
            if param=='nvnhs':
                pl.ylabel('# Prefix Groups',fontsize=32)
                #pl.xlim(0,10000+100)
                ax.set_ylim(ymin=1)
                ax.set_xlim(xmin=0)
            elif param=='mdsTime':
                pl.ylabel('Time(seconds)',fontsize=32)
                #pl.xlim(0,10000+100)
                ax.set_ylim(ymin=1)
                ax.set_xlim(xmin=0)
                
            ax.grid(True)
            
            plot_name=option+'_'+param+'.eps'
            plot_name_png=option+'_'+param+'.png'
            pl.savefig(plot_name)
            pl.savefig(plot_name_png)
 
    elif option=='prefixBM':
        print "plotting "+str(option)+" result"
        #dname="composeBM_matapan.dat"
        data=json.load(open(dname, 'r'))
        data=restructureData(data)
        params=['#vnhs']
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
                    tmp[float(hdr)]=v[hdr]
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
            markers=['o','*','^','s','d','3','d','o','*','^','1','4']
            p1=[]
            i=0
            leg=data[param].keys()
            leg.sort(reverse=True)
            legnd=[]
            for k in leg:
                #leg.append(float(k))
                x=float(k)*100
                legnd.append('f= '+str(x)+'%')
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
                #pl.text(xlab[int(float(len(xlab)/2))],20+a[int(float(len(a)/2))],'frac= '+str(k),fontsize=20,horizontalalignment='center')
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
            leg.sort() 
            pl.legend((p),legnd,'upper left',prop={'size':32})
            pl.xlabel('# Prefixes',fontsize=32)
            if param=='#vnhs':
                pl.ylabel('# Prefix Groups',fontsize=32)
                pl.xlim(0,10000+100)
                ax.set_ylim(ymin=1)
                #pl.ylim(-10,500)
                
            ax.grid(True)
            
            plot_name=option+'_'+param+'.eps'
            plot_name_png=option+'_'+param+'.png'
            pl.savefig(plot_name)
            pl.savefig(plot_name_png)
            
                

if __name__ == '__main__':
    main(sys.argv[1]) 