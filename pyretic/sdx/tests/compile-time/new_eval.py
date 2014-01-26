#############################################
# author: Arpit Gupta (glex.qsd@gmail.com)  #
#############################################
"""
Updated Script to evaluate the performance of different composition schemes
"""

#from predicateBM import *
from PgenPset import *
import os,json,sys
import subprocess
from multiprocessing import Process, Queue

def UPDATEDcompilationTimeExperiment(ntot,nprefixes,nfields,q=None):
    print "Starting the experiment with parameters: ",ntot,nprefixes,nfields,len(policy_parl)
    print '...'
    startexp=time.time()
    # define the parameters
    ntot=ntot # total number of participants
    fmult=0.05  # fraction of participants with multiple ports
    nmult=int(ntot*fmult)
    nports=2 # number of ports for the participants with multiple ports 
    nprefixes=nprefixes # total # of prefixes
    fractionGroup=0.1 # fraction of prefix groups wrt total prefixes
    
    #Np=100 #total number of prefixes
    advertisers=[(0.05,1),(0.15,0.20),(0.80,0.01)]
    partTypes=[0.05,0.15,0.05,0.75]
    frand=0.025
    nfields=nfields
    nval=50
    
    
    sdx_participants=generate_sdxglobal(ntot,nmult,nports) 
       
    (sdx,participants) = sdx_parse_config('sdx_global.cfg')
    # get pfx groups for writing SDX policies
    #sdx.pfxgrp=getPfxGroup(nprefixes,fractionGroup)
    #print sdx.pfxgrp
    #print len(sdx.pfxgrp.keys())
    
    update_paramters(sdx,ntot,nports)
    #print sdx.participant_to_ebgp_nh_received    
    update_bgp(sdx,advertisers,nprefixes,ntot)
    sdx.pfxgrp=sdx.prefixes
    #print sdx.participant_to_ebgp_nh_received 
    
    #print sdx.prefix_2_part
      
    
    
    generatePolicies(sdx,participants,ntot,nmult,partTypes,frand,nfields,nval,headerFields,fieldValues)
    
    
    start=time.time()
    vnh_assignment(sdx,participants)
    augmentTime1=time.time()-start
    print "Policy Augmentation: ",time.time()-start
    decompose=True
    if decompose==True:
        
        nRules,compileTime,augmentTime2=ddisjointCompose(sdx)
    else:
        augmentTime2=0
        nRules,compileTime=disjointCompose(sdx)
    print nRules,compileTime,augmentTime1,augmentTime2
    augmentTime=float(augmentTime2)/len(sdx.VNH_2_IP.keys())+augmentTime1
    
    # Get Compiler's cache size
    s1=total_size(policy_parl,verbose=False)
    s2=total_size(policy_seq,verbose=False)
    s3=total_size(disjoint_cache,verbose=False)
    cacheSize=s1+s2+s3
    print "Iteration completed in: ",time.time()-startexp
    if q==None:
        return (nRules,augmentTime,compileTime,cacheSize)
    else:
        q.put((nRules,augmentTime,compileTime,cacheSize))
    

def updateBurstExperiment(mode,ntot,nprefixes,nfields,nUpdates,dataPoints=1,q=None):
    print "Starting the experiment with parameters: ",mode,ntot,nprefixes,nUpdates,len(policy_parl)
    print '...'
        # define the parameters
    ntot=ntot # total number of participants
    fmult=0.05  # fraction of participants with multiple ports
    nmult=int(ntot*fmult)
    nports=2 # number of ports for the participants with multiple ports 
    nprefixes=nprefixes # total # of prefixes
    fractionGroup=0.1 # fraction of prefix groups wrt total prefixes
    
    #Np=100 #total number of prefixes
    advertisers=[(0.05,1),(0.15,0.20),(0.80,0.01)]
    partTypes=[0.05,0.15,0.05,0.75]
    frand=0.025
    nfields=nfields
    nval=50
    biasfactor=10
    
    
    sdx_participants=generate_sdxglobal(ntot,nmult,nports) 
       
    (sdx,participants) = sdx_parse_config('sdx_global.cfg')
    
    update_paramters(sdx,ntot,nports)
    #print sdx.participant_to_ebgp_nh_received    
    update_bgp(sdx,advertisers,nprefixes,ntot)
    sdx.pfxgrp=sdx.prefixes
    generatePolicies(sdx,participants,ntot,nmult,partTypes,frand,nfields,nval,headerFields,fieldValues)
    
    
    start=time.time()
    vnh_assignment(sdx,participants)
    print "Policy Augmentation: ",time.time()-start
    
    
    compile_Policies(participants)
    start=time.time()
    nRules,compileTime,augmentTime2=ddisjointCompose(sdx)
    print nRules,compileTime
    
    # Get Compiler's cache size
    s1=total_size(policy_parl,verbose=False)
    s2=total_size(policy_seq,verbose=False)
    s3=total_size(disjoint_cache,verbose=False)
    cacheSize=s1+s2+s3
    print "Cache sizes: ",cacheSize
    
    # Process BGP Updates
    updateEval=True    
    if updateEval==True:        
        deltaRules={}
        updateCompileTime={}
        for up in nUpdates:         
            
            deltaRules[up]=[]
            updateCompileTime[up]=[]       
            for dp in range(dataPoints):
                print "iteration: ",dp+1                       
                nRules1,compileTime1=addVNH(sdx,up,biasfactor,advertisers,ntot)
                #deltaRules[up].append(nRules1-nRules)
                deltaRules[up].append(nRules1)
                updateCompileTime[up].append(compileTime1)

    if q==None:
        return (nRules,compileTime,cacheSize,deltaRules,updateCompileTime)
    else:
        q.put((nRules,compileTime,cacheSize,deltaRules,updateCompileTime))

            

def compilationTimeExperiment(mode,ntot,nprefixes,nfields,fractionGroup,q=None):
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
    
    compile_Policies(participants)
    
    start=time.time()
    nRules,compileTime=disjointCompose(sdx)
    print "# flow-rules",nRules," compile-time:",compileTime

    
    if q==None:
        return augmentTime,mdsTime,nVNHs,nRules,compileTime
    else:
        q.put((augmentTime,mdsTime,nVNHs,nRules,compileTime))

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
    #augmentTime,mdsTime=prefixGroupExperiment('dlsm',500,800,1,0.01)
    #nRules,compileTime,cacheSize,deltaRules,updateCompileTime=updateBurstExperiment('dlsm',40,10,1,[10,20,30,40,50])
    #print nRules,compileTime,cacheSize,deltaRules,updateCompileTime
    nRules,augmentTime,compileTime,cacheSize=UPDATEDcompilationTimeExperiment(80,10,1)
    print nRules,augmentTime,compileTime,cacheSize