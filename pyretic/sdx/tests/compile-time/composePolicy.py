#############################################
# author: Arpit Gupta (glex.qsd@gmail.com)  #
#############################################
"""
Script to evaluate the performance of different composition schemes
"""

from predicateBM import *
import os,json,sys
import subprocess
from multiprocessing import Process, Queue

def composeExperiment(mode,ntot,nprefixes,nfields,q=None):
    print "Starting the experiment with parameters: ",mode,ntot,nprefixes,nfields,len(policy_parl)
    print '...'

    # Initialize the parameters
    fmult=0.2  # fraction of participants with multiple ports
    nmult=int(ntot*fmult)
    nports=2 # number of ports for the participants with multiple ports 
    advertisers=[(0.05,1),(0.15,0.20),(0.80,0.01)]
    partTypes=[0.05,0.15,0.05,0.75]
    frand=0.025
    nval=5
    
    sdx_participants=generate_sdxglobal(ntot,nmult,nports) 
       
    (sdx,participants) = sdx_parse_config('sdx_global.cfg')
    
    update_paramters(sdx,ntot,nports)
    
    update_bgp(sdx,advertisers,nprefixes,ntot)    
    
    generatePolicies(sdx,participants,ntot,nmult,partTypes,frand,nfields,nval,headerFields,fieldValues)
    
    vnh_assignment(sdx,participants)
    
    compile_Policies(participants)
    
    if mode=='dlsm':
        nRules,compileTime=disjointCompose(sdx)
    elif mode=='lsm':
        nRules,compileTime=lsmCompose(sdx)
    elif mode=='naive':
        nRules,compileTime=naiveCompose(sdx)
    else:
        print "Error: incorrect composition mode"
    
        
    print "rules: ",nRules," time: ",compileTime   
    
    if q==None:
        return nRules,compileTime
    else:
        q.put((nRules,compileTime))
    
    
    
    

if __name__ == '__main__':
    composeExperiment('dlsm',40,20,1)
    
    
    