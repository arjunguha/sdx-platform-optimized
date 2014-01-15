#############################################
# author: Arpit Gupta (glex.qsd@gmail.com)  #
#############################################
"""
Microbenchmark script for varying number of predicate's header fields
"""
from common import *
from pgen_noVerify import *
import sys,json
verify=False

headerFields=['dstport','srcport','srcip']
fieldValues={'dstport':range(1,101),'srcport':range(1,101),
             'srcip':list(IPNetwork('172.0.0.1/26'))}

def experiment(ntot,nprefixes,nfields,q=None):
    print "Starting the experiment with parameters: ",ntot,nprefixes,nfields,len(policy_parl)
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
    
    nRules,compileTime=disjointCompose(sdx)
    if q==None:
        return nRules,compileTime
    else:
        q.put((nRules,compileTime))
    

    
    

if __name__ == '__main__':
    nRules,compileTime=experiment(10,10,0)
    print nRules,compileTime