#############################################
# author: Arpit Gupta (glex.qsd@gmail.com)  #
#############################################
"""
Generic benchmarking data collection script
"""

from predicateBM import *
import os,json,sys
import subprocess
from multiprocessing import Process, Queue

dataPoints=2

def getKey(ntot,npfx):
    return str(ntot)+","+str(npfx)

def main(option):
    if option=='predicate':
        data={}
        print 'Running Predicate Experiment'
        # number of participants and prefix groups
        #partpfx=[(20,50),(40,100),(100,100)]
        partpfx=[(10,5),(10,10)]
        # header fields
        nheaders=range(4)
        #data['partpfx']=partpfx
        data['time']={}
        data['space']={}        
        for ntot,npfx in partpfx:
            k=getKey(ntot,npfx)
            data['time'][k]={}
            data['space'][k]={}
            for nfields in nheaders:
                
                data['time'][k][nfields]=[]
                data['space'][k][nfields]=[]
                for dp in range(dataPoints):
                    print "iteration: ",dp+1
                    q=Queue()
                    p=Process(target=experiment, args=(ntot,npfx,nfields,q))
                    p.start()
                    qout=q.get()
                    p.join()
                    nRules,compileTime=qout
                    #nRules,compileTime=experiment(ntot,npfx,nfields)
                    data['time'][k][nfields].append(compileTime)
                    data['space'][k][nfields].append(nRules)
                    
        with open('predicateBM.dat', 'w') as outfile:
            json.dump(data,outfile,ensure_ascii=True,encoding="ascii")          
        print data 
        
if __name__ == '__main__':
    main(sys.argv[1])  
    