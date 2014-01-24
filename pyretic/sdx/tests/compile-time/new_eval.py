#############################################
# author: Arpit Gupta (glex.qsd@gmail.com)  #
#############################################
"""
Updated Script to evaluate the performance of different composition schemes
"""

#from predicateBM import *
from newPgen import *
import os,json,sys
import subprocess
from multiprocessing import Process, Queue

def prefixGroupExperiment(mode,ntot,nprefixes,nfields,fractionGroup,q=None):
    print "Starting the experiment with parameters: ",mode,ntot,nprefixes,nfields,fractionGroup,len(policy_parl)
    print '...'
    start=time.time()
    # define the parameters
    ntot=ntot # total number of participants
    fmult=0.05  # fraction of participants with multiple ports
    nmult=int(ntot*fmult)
    nports=2 # number of ports for the participants with multiple ports 
    nprefixes=nprefixes # total # of prefixes
    fractionGroup=fractionGroup # fraction of prefix groups wrt total prefixes
    
    #Np=100 #total number of prefixes
    advertisers=[(0.05,1),(0.15,0.20),(0.80,0.01)]
    partTypes=[0.05,0.15,0.05,0.75]
    frand=0.025
    nfields=nfields
    nval=50
    
    
    sdx_participants=generate_sdxglobal(ntot,nmult,nports) 
       
    (sdx,participants) = sdx_parse_config('sdx_global.cfg')
    # get pfx groups for writing SDX policies
    sdx.pfxgrp=getPfxGroup(nprefixes,fractionGroup)
    #print len(sdx.pfxgrp.keys())
    update_paramters(sdx,ntot,nports)
    
    update_bgp(sdx,advertisers,nprefixes,ntot) 
    #print sdx.prefix_2_part
      
    
    
    generatePolicies(sdx,participants,ntot,nmult,partTypes,frand,nfields,nval,headerFields,fieldValues)
    print "Time to configure SDX: ",time.time()-start
    
    start=time.time()
    mdsTime,nVNHs=vnh_assignment(sdx,participants)
    augmentTime=time.time()-start
    print "Policy Augmentation: ",augmentTime," MDS Time: ",mdsTime," # VNHs: ",nVNHs

    
    if q==None:
        return augmentTime,mdsTime,nVNHs
    else:
        q.put((augmentTime,mdsTime,nVNHs))
    
    
if __name__ == '__main__':
    augmentTime,mdsTime=prefixGroupExperiment('dlsm',500,800,1,0.01)
    