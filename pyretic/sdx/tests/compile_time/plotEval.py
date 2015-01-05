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
from matplotlib.ticker import MaxNLocator
my_locator = MaxNLocator(6)

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
    #dname='mdsTrace_linx__Mon27Jan2014204022.dat'
    #dname='mdsTrace_decix__Mon27Jan2014211640.dat'
    dname='bgpUpdate_Wed29Jan2014031457.dat'
    dname='UPDATEDcompileTime_Wed29Jan2014023417.dat'
    dname='mdsTrace_Wed29Jan2014173721.dat'
    dname='bgpUpdate_Wed29Jan2014062818.dat'

    if option=='initCompile':
        print "plotting "+str(option)+" result"
        print "plotting "+str(option)+" result"
        dname='foo'
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
                    tmp_dat=[]
                    if param=='cacheSize':
                        for dat in v[hdr]:
                            # convert into MB
                            tmp_dat.append(int(float(dat)/1048576))
                        v[hdr]=tmp_dat
                    elif param=='nrules':
                        print 'nrules'
                        for dat in v[hdr]:
                            tmp_dat.append(int(float(dat)/1000))
                        v[hdr]=tmp_dat
                    total, average, median, standard_deviation, minimum, maximum, confidence=stats(v[hdr])
                    print median,standard_deviation
                    #median=average
                    tmp_median.append(median)
                    tmp_stddev.append(standard_deviation)
                print "median: ",tmp_median
                data[param][k]['median']=tmp_median
                data[param][k]['stddev']=tmp_stddev

            fig = plt.figure()
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

                legnd.append(''+str(int(k))+' Participants')
                a=data[param][k]['median']
                v=data[param][k]
                err=data[param][k]['stddev']
                p1.append([])
                print sorted(v.iterkeys())
                xlab.sort()
                print "xlab: ",xlab
                p1[i]=pl.errorbar(xlab,a,yerr=err,markerfacecolor=color_n[i],
                              color='k', ecolor='k',marker=markers[i],
                              label=k)
                #pl.text(xlab[int(float(len(xlab)/2))],20+a[int(float(len(a)/2))],'frac= '+str(k),fontsize=20,horizontalalignment='center')
                i+=1
            p=[]
            i=0
            for k in data[param].keys():
                p.append(p1[i][0])
                i+=1
            """
            for tick in ax.xaxis.get_major_ticks():
                tick.label.set_fontsize(24)
            for tick in ax.yaxis.get_major_ticks():
                tick.label.set_fontsize(24)
            """
            leg.sort()
            pl.legend((p),legnd,'upper left')
            pl.xlabel('Prefix Groups')
            pl.xlim(1,1010)
            if param=='cacheSize':
                pl.ylabel('Megabytes')
                ax.set_xlim(xmin=1)
                #ax.set_ylim(ymin=-1)
            elif param=='cTime':
                pl.ylabel('Time (seconds)')
                ax.set_xlim(xmin=1)
                #ax.set_ylim(ymin=-1)

            elif param=='augmentTime':
                pl.ylabel('Time (seconds)')
                ax.set_xlim(xmin=1)
                #ax.set_ylim(ymin=-1)

            elif param=='nrules':
                pl.ylabel(r'Flow Rules ($\times$ 1000)')
                ax.set_xlim(xmin=1)
                #ax.set_ylim(ymin=-1)
                #pl.xlim(0,51)
                #ax.set_ylim(ymin=1)

            ax.yaxis.set_major_locator(my_locator)
            ax.grid(True)
            plt.tight_layout()
            plot_name=option+'_'+param+'.eps'
            plot_name_png=option+'_'+param+'.png'
            pl.savefig(plot_name)
            pl.savefig(plot_name_png)

    elif option=='mdsScatter':
        print "plotting "+str(option)+" result"
        dname="mdsTrace_Wed29Jan2014193801.dat"
        data=json.load(open(dname, 'r'))
        #data=restructureData(data)
        params=['scatter']
        xlab=[]
        for param in params:
            print "plotting for the param: ",param

            inSize={}
            avgSize={}
            mdsTime={}


            tplList=data[param]
            legnd=[]
            for tpl in tplList:
                print tpl
                if tpl[0] not in legnd:
                    legnd.append(tpl[0])
                if tpl[0] not in inSize:
                    inSize[tpl[0]]=[]
                if tpl[0] not in avgSize:
                    avgSize[tpl[0]]=[]
                if tpl[0] not in mdsTime:
                    mdsTime[tpl[0]]=[]
                inSize[tpl[0]].append(tpl[1]-2)
                avgSize[tpl[0]].append(tpl[2])
                mdsTime[tpl[0]].append(15*3.14*tpl[3]*tpl[3])

            legnd.sort(reverse=True)
            fig = plt.figure(figsize=(12,12))
            ax = fig.add_subplot(1,1,1)
            color_n=['g','m','c','r','b','k','w']
            markers=['o','*','^','s','d','3','d','o','*','^','1','4']
            p1=[]
            i=0
            print inSize,avgSize,mdsTime

            for leg in legnd:
                p1.append([])


                p1[i]=pl.scatter(inSize[leg],avgSize[leg],s=mdsTime[leg],c=color_n[i],linewidths=2,edgecolor='k',alpha=0.75)
                p=[]
                i+=1

            i=0


            for tick in ax.xaxis.get_major_ticks():
                tick.label.set_fontsize(24)
            for tick in ax.yaxis.get_major_ticks():
                tick.label.set_fontsize(24)
            pl.xlabel('Input Prefix Sets',fontsize=32)

            pl.ylabel('Average Size',fontsize=32)
                #pl.xlim(0,51)
                #ax.set_ylim(ymin=1)

            ax.grid(True)

            plot_name=option+'_'+param+'.eps'
            plot_name_png=option+'_'+param+'.png'
            pl.savefig(plot_name)
            pl.savefig(plot_name_png)

    elif option=='bgpUpdateCDF':
        print "plotting "+str(option)+" result"
        dname='bgpUpdate_Wed29Jan2014062818.dat'
        data=json.load(open(dname, 'r'))
        #data=restructureData(data)
        params=['updateTime']
        xlab=[]
        for param in params:
            print "plotting for the param: ",param
            raw={}
            fig = plt.figure()
            ax = fig.add_subplot(1,1,1)
            color_n=['g','m','c','r','b','k','w']
            markers=['o','*','^','s','d','3','d','o','*','^','1','4']
            linestyles=[ '--',':','-','-.']
            p1=[]
            legnd=[]
            i=0
            for key in data[param]:
                print key
                raw[key]=data[param][key]['1']
                tmp=[]
                for elem in raw[key]:
                    tmp.append(elem*1000)
                raw[key]=tmp

                raw[key].sort(reverse=True)
                #print raw[key]
                raw[key]=filter(lambda x: x<=1000,raw[key])

                num_bins=10000
                counts, bin_edges = np.histogram(raw[key],bins=num_bins,normed=True)
                print bin_edges
                cdf=np.cumsum(counts)
                scale = 1.0/cdf[-1]
                cdf=cdf*scale
                print cdf

                p1.append([])
                legnd.append(''+str(int(key))+' Participants')

                p1[i]=pl.plot(bin_edges[1:],cdf,label=key,color=color_n[i],linestyle=linestyles[i])
                i+=1

            i=0
            p=[]
            for k in data[param].keys():
                p.append(p1[i][0])
                i+=1
            """
            for tick in ax.xaxis.get_major_ticks():
                tick.label.set_fontsize(24)
            for tick in ax.yaxis.get_major_ticks():
                tick.label.set_fontsize(24)
            """

            pl.legend((p),legnd,'lower right')
            pl.xlabel('Time (milliseconds)')

            #pl.ylabel('CDF',fontsize=32)
            #pl.xlim(0,51)
            ax.set_ylim(ymin=0.01)

            ax.grid(True)
            plt.tight_layout()
            plot_name=option+'_'+param+'.eps'
            plot_name_png=option+'_'+param+'.png'
            pl.savefig(plot_name)
            pl.savefig(plot_name_png)

    elif option=='bgpUpdate':
        print "plotting "+str(option)+" result"
        dname="bgpUpdate_Wed29Jan2014031457.dat"
        data=json.load(open(dname, 'r'))
        #data=restructureData(data)
        params=['deltaRules']
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

            fig = plt.figure()
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

                legnd.append(''+str(int(k))+' Participants')
                a=data[param][k]['median']
                v=data[param][k]
                err=data[param][k]['stddev']
                p1.append([])
                print sorted(v.iterkeys())
                xlab.sort()
                print "xlab: ",xlab
                print "a: ",a
                p1[i]=pl.errorbar(xlab,a,yerr=err,markerfacecolor=color_n[i],
                              color='k', ecolor='k',marker=markers[i],
                              label=k)
                #pl.text(xlab[int(float(len(xlab)/2))],20+a[int(float(len(a)/2))],'frac= '+str(k),fontsize=20,horizontalalignment='center')
                i+=1
            p=[]
            i=0
            for k in data[param].keys():
                p.append(p1[i][0])
                i+=1
            """
            for tick in ax.xaxis.get_major_ticks():
                tick.label.set_fontsize(24)
            for tick in ax.yaxis.get_major_ticks():
                tick.label.set_fontsize(24)
            """
            leg.sort()
            pl.legend((p),legnd,'upper left')
            pl.xlabel('Burst Size (BGP Updates)')
            if param=='deltaRules':
                pl.ylabel(' Additional Rules')
                #pl.xlim(0,51)
                #ax.set_ylim(ymin=1)
            elif param=='updateTime':
                pl.ylabel('Time (seconds)')
                #pl.xlim(0,51)
                #ax.set_ylim(ymin=0)

            ax.yaxis.set_major_locator(my_locator)
            ax.grid(True)
            plt.tight_layout()
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
                legnd.append(''+str(int(k))+' Participants')
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
            pl.xlabel(' Prefixes',fontsize=32)
            if param=='nvnhs':
                pl.ylabel(' Prefix Groups',fontsize=32)
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

    elif option=='MDS-decix':
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

                legnd.append('Participants='+str(int(k))+'')
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
            pl.xlabel(' Prefixes',fontsize=32)
            if param=='nvnhs':
                pl.ylabel(' Prefix Groups',fontsize=32)
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
    elif option=='MDS-pg':
        print "plotting "+str(option)+" result"
        dname='mdsTrace_Wed29Jan2014195955.dat'
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

            fig = plt.figure()
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
            tmp=[]
            for elem in xlab:
                tmp.append(elem)
            xlab=tmp
            leg=filter(lambda x:x<=150,leg)
            for k in leg:
                #leg.append(float(k))

                legnd.append(''+str(int(k))+' Participants')
                k=unicode(k)
                a=data[param][k]['median']
                v=data[param][k]
                err=data[param][k]['stddev']
                p1.append([])
                print sorted(v.iterkeys())
                xlab.sort()
                print "xlab: ",xlab
                p1[i]=pl.errorbar(xlab,a,yerr=err,markerfacecolor=color_n[i],
                              color='k',ecolor='k',marker=markers[i],
                              label=k)
                #pl.text(xlab[int(float(len(xlab)/2))],20+a[int(float(len(a)/2))],'frac= '+str(k),fontsize=20,horizontalalignment='center')
                i+=1
            p=[]
            i=0
            for k in leg:
                p.append(p1[i][0])
                i+=1
            """
            for tick in ax.xaxis.get_major_ticks():
                tick.label.set_fontsize(24)
            for tick in ax.yaxis.get_major_ticks():
                tick.label.set_fontsize(24)
            """
            leg.sort()

            pl.xlabel('Prefixes')
            #pl.xlim(0,26)
            if param=='nvnhs':
                pl.legend((p),legnd,'lower right')
                pl.ylabel(' Prefix Groups')
                #pl.xlim(0,10000+100)
                ax.set_ylim(ymin=1)
                ax.set_xlim(xmin=0)
            elif param=='mdsTime':
                pl.legend((p),legnd,'upper left')
                pl.ylabel('Time(seconds)')
                #pl.xlim(0,10000+100)
                ax.set_ylim(ymin=1)
                ax.set_xlim(xmin=0)

            ax.yaxis.set_major_locator(my_locator)
            #ax.xaxis.set_major_locator(my_locator)
            ax.grid(True)
            plt.tight_layout()
            plot_name=option+'_'+param+'.eps'
            plot_name_png=option+'_'+param+'.png'
            pl.savefig(plot_name)
            pl.savefig(plot_name_png)

    elif option=='MDS-amsix':
        print "plotting "+str(option)+" result"
        dname='mdsTrace_Wed29Jan2014195955.dat'
        data=json.load(open(dname, 'r'))
        #data=restructureData(data)
        params=['mdsTime']
        xlab=[]
        for param in params:
            print "plotting for the param: ",param
            for k,v in data[param].iteritems():
                print k
                if k>=5000:
                    tmp_median=[]
                    tmp_stddev=[]
                    print v.keys()
                    tmp={}
                    for hdr in v:
                        tmp[float(hdr)]=v[hdr]
                    v=tmp
                    v.keys().sort()
                    xlab=filter(lambda x: x>=5000,v.keys())

                    for hdr in sorted(v.iterkeys()):
                        print hdr,v[hdr]
                        total, average, median, standard_deviation, minimum, maximum, confidence=stats(v[hdr])
                        print median,standard_deviation
                        #median=average
                        if hdr>=5000:
                            tmp_median.append(median)
                            tmp_stddev.append(standard_deviation)
                    print "median: ",tmp_median
                    data[param][k]['median']=tmp_median
                    data[param][k]['stddev']=tmp_stddev
            bubbleSize=getBsize(data)
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
            #leg=[100,50,200,150]
            for k in leg:
                #leg.append(float(k))
                print 'legend:',leg
                legnd.append(''+str(int(k))+' Participants')
                k=unicode(k)
                a=data[param][k]['median']
                v=data[param][k]
                err=data[param][k]['stddev']
                p1.append([])
                print sorted(v.iterkeys())
                xlab.sort()
                print "xlab: ",xlab
                print bubbleSize[int(k)]
                #p1[i]=pl.plot(xlab,a,c=color_n[i],marker='o')
                p1[i]=pl.plot(xlab,a,markerfacecolor=color_n[i],markeredgecolor='none',
                              color='none',markersize=20,marker='o',linewidth=2.0)
                pl.scatter(xlab,a,s=bubbleSize[int(k)],c=color_n[i],linewidths=2,edgecolor='none',alpha=1.0)



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
            #pl.legend((p),legnd,'upper left',prop={'size':32})
            pl.legend((p),legnd,'upper left',prop={'size':24})
            pl.xlabel('# Prefixes',fontsize=32)
            if param=='nvnhs':
                pl.ylabel('# Prefix Groups',fontsize=32)
                #pl.xlim(0,10000+100)
                ax.set_ylim(ymin=1)
                ax.set_xlim(xmin=0)
            elif param=='mdsTime':
                pl.ylabel('VNH Computation Time (seconds)',fontsize=32)
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


def getBsize(data):
    bsize={}
    pfxes=[]
    for tpl in data['scatter']:
        pfx=tpl[0]
        if pfx>=5000:
            part=getNear(tpl[1]-2,[50,100,150,200])
            size=tpl[2]
            if part not in bsize:
                bsize[part]={}
            if pfx not in bsize[part]:
                bsize[part][pfx]=[]
            if pfx not in pfxes:
                pfxes.append(pfx)

            bsize[part][pfx].append(size)
    pfxes.sort()
    for k in bsize:
        for pfx in bsize[k]:
            total, average, median, standard_deviation, minimum, maximum, confidence=stats(bsize[k][pfx])
            bsize[k][pfx]=0.00015*3.14*median**2
    final={}
    for k in bsize:
        final[k]=[]
        for pfx in pfxes:
            final[k].append(bsize[k][pfx])

    return final

def getNear(a,lst):
    diff=1000
    out=0
    for elem in lst:
        tmp=elem-a
        if tmp<diff and tmp>=0:
            diff=tmp
            out=elem
    return out

if __name__ == '__main__':
    main(sys.argv[1])