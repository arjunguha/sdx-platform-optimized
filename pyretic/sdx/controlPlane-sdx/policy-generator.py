#############################################
# author: Arpit Gupta (glex.qsd@gmail.com)  #
#############################################

from common import *
from size import *
import sys,json
verify=False
debug=False
uniformRIB=True

from multiprocessing import Process, Queue
import multiprocessing as mp
import copy

headerFields=['dstport','srcport','srcip']
fieldValues={'dstport':range(1,101),'srcport':range(1,101),
             'srcip':list(IPNetwork('172.0.0.1/26'))}

def divideParticipants(partTypes, ntot):
    nparts=[]
    for i in range(len(partTypes)-1):
        tmp=int(partTypes[i]*ntot)
        if tmp==0:
            tmp=1
        nparts.append(tmp)
    nparts.append(ntot-sum(nparts))
    n1=nparts[0]
    n2=sum(nparts[0:2])
    n3=sum(nparts[0:3])
    
    return n1,n2,n3,nparts


def normalizePrefixSets(sdx, nparts, fracPG):
    tmp=sdx.pfxgrp.keys()
    div=int(float(len(tmp))/nparts[0])
    if debug==True: print 'DIV:',div
    part2prefixset={}
    for i in range(nparts[0]-1):
        k=i*div
        part2prefixset[i+1]=tmp[k:k+div]
    k=(nparts[0]-1)*div
    part2prefixset[nparts[0]]=tmp[k:]
    #print "Before Normalization: ",part2prefixset
    N=len(sdx.pfxgrp.keys())
    N1=int(N*fracPG)
    if N1==0:
        N1=1
    #N1=5
    p=len(part2prefixset[1])
    #print N1,p
    if debug==True: print 'Before normalization, part2prefixset: ',part2prefixset
    if p<N1:
        # Add more prefixes to maintain that each participant has policies for at least 5%
        #print "Needs Change"
        for k in part2prefixset:
            if k!=n1:
                new=random.sample(tmp,N1-p)
                part2prefixset[k]+=new
    if debug==True: print 'Before normalization, part2prefixset: ',part2prefixset


def updateHeaderFields(headerFields, fieldValues, nval, nfields):
    """
        Logic for selecting the header fields and their possible values.
    """
    # Randomly sample which header fields will be used for participant's "Outbound" policies
    headerFields=random.sample(headerFields,nfields)
    
    # Randomly sample the header field values for each field
    for k in fieldValues:
        fieldValues[k]=random.sample(fieldValues[k],nval)
    
    
    # Repeating the same thing for Inbound policies. Currently ignoring inbound policies matching on dstip
    headerFieldInbound=random.sample(headerFields,nfields)
    for k in fieldValues:
        fieldValues[k]=random.sample(fieldValues[k],nval)
    
    """
    # Currently ignoring inbound policies matching on dstip
    headerFieldInbound.append('match_prefixes_set')
    vals=[]
    for k in sdx.pfxgrp.keys():
        print k
        vals.append(sdx.pfxgrp[k])
    fieldValues['match_prefixes_set']=vals
    """ 
    
    return headerFields, headerFieldInbound, fieldValues


def generatePolicies(sdx,participants,ntot,nmult,partTypes,frand,nfields,
                     nval,headerFields,fieldValues):
    
    
    """ Update the header fields to be used for the generated policies"""
    headerFields, headerFieldInbound, fieldValues = updateHeaderFields(headerFields, 
                                                                       fieldValues, nval, nfields)    
    if debug==True: print "Samples header field values: ",fieldValues
    
    """
        Logic to divide the policies for top eyeballs, top content and others
        1: Tier 1 ISPs (5%) (1->n1)
        2: Tier 2 ISPs (15%) (n+1->n2)
        3: Top Content (5%) (n2+1->n3)
        4: Others (useless fellows) n3+
    """
    n1, n2, n3, nparts = divideParticipants(partTypes, ntot)
    if debug==True: print "Participant Division: ",n1,n2,n3
    
    """ 
        Logic to equally divide prefix sets announced by each Tier1 ISPs.
        Why? This steps are required to avoid performance bias where we increase # of participants
        for same # of prefix sets. This division approach ensures that there are atleast 
        certain ("fracPG") fraction of prefixes for which each tier 1 participant has policies. 
    """
    
    fracPG=0.06 # 6%
    # part2prefixset: dictionary which maps participants to dstip prefixes used for its outbound policies
    part2prefixset = normalizePrefixSets(sdx, nparts, fracPG)

    
    
    
    # Logic to equally divide the eyeballs among the content providers
    tmp=range(1,n1+1)
    div=int(float(len(tmp))/(n3-n2))
    if debug==True: print "new div",div
    eb={}
    kys=range(n2+1,n3)
    for i in kys:
        k=(i-(n2+1))*div
        eb[i]=tmp[k:k+div]
    k=(n3-n2-1)*div
    eb[n3]=tmp[k:]
    if debug==True: print "EB:",eb
    
    if debug==True: print "Prefix Set: ",part2prefixset
    
    nrand=int(frand*ntot)
    if nrand==0:
        nrand=1
    #nrand=2
    intensityFactor=2 # more rules for top eyeballs and content providers    
    inbound={}
    for participant in sdx.participants:
        sdx.part2pg[participant.id_]=[]
        policy=drop
        pdict={}
        
        #debug=False
        if debug==True: print 'participant: ',participant.id_,sdx.participant_2_port[participant.id_][participant.id_]
        inbound[participant.id_]=[]
        if int(participant.id_)<=n1:
            
            if debug==True: print "policies for Tier1 ISPs"
            
            # inbound policies for traffic coming from top content folks  
            topContent=random.sample(range(n2+1,n3+1),nrand)        
            for pid in topContent:
                tmp=getPred(headerFieldInbound,fieldValues,nfields)
                if debug==True: print "tier 1 inbound pred",tmp
                assert(isinstance(tmp,sequential))
                pred=tmp.policies[0]
                if isinstance(pred,match_prefixes_set)==True:
                    pfx=(list(pred.pfxes))[0]
                    inbound[participant.id_].append(pfx)
                pdict[tmp]=fwd(random.choice(participant.phys_ports).id_)
                
            
            #inbound policies for advertised IP prefix sets
            #This ensures that all prefix sets have at-least one rule
            #print part2prefixset[int(participant.id_)]
            """
            for pfxset in part2prefixset[int(participant.id_)]:
                inbound[participant.id_].append(pfxset)
                pdict[drop|(match_prefixes_set([pfxset]))]=fwd(random.choice(participant.phys_ports).id_)
                
            """
            """
            # outbound policies for traffic to randomly selected transit 
            tier2=random.sample(range(n1+1,n2+1),nrand) 
            for pid in tier2:
                announced=sdx.prefixes_announced['pg1'][unicode(pid)]
                pfxset=random.choice(announced)
                tmp=getPred(headerFields,fieldValues,nfields)
                tmp=(match_prefixes_set([pfxset])>>tmp)
                pdict[tmp]=fwd(participant.peers[str(pid)].participant.phys_ports[0].id_)
            
            """       
                        
        elif int(participant.id_)>n1 and int(participant.id_)<=n2:
            if debug==True: print "policies for Tier 2 ISPs"
            # inbound policies for few top content participants
            topContent=random.sample(range(n2+1,n3+1),nrand)
            for pid in topContent:
                tmp=getPred(headerFieldInbound,fieldValues,nfields)
                if debug==True: print "tier 2 inbound pred",tmp.policies
                assert(isinstance(tmp,sequential))
                pred=tmp.policies[0]
                if isinstance(pred,match_prefixes_set)==True:
                    pfx=(list(pred.pfxes))[0]
                    inbound[participant.id_].append(pfx)
                pdict[tmp]=fwd(random.choice(participant.phys_ports).id_)
                        
            # outbound policies for few top eyeballs
            
            topEyeballs=random.sample(range(1,n1),nrand)
            for pid in topEyeballs:
                # "part: ",pid
                announced=sdx.pfxgrp.keys()
                # currently selecting only one dstip prefix set for writing specific rules
                pfxset=random.choice(announced)
                tmp=getPred(headerFields,fieldValues,nfields)
                tmp=(match_prefixes_set(sdx.pfxgrp[pfxset])>>tmp) 
                sdx.part2pg[participant.id_].append(sdx.pfxgrp[pfxset][0])              
                pdict[tmp]=fwd(participant.peers[str(pid)].participant.phys_ports[0].id_)
           
            
        elif int(participant.id_)>n2 and int(participant.id_)<=n3:
            if debug==True: print "policies for content providers"
            
            # outbound policies for top eyeballs
            #for pid in range(1,n1+1):
            #topeyeballs=random.sample(range(1,n1+1),nrand) 
            topeyeballs=eb[int(participant.id_)]
            
            for pid in topeyeballs:
                #print "part2prefixset:",part2prefixset[pid],topeyeballs
                #print len(part2prefixset[pid]),part2prefixset
                if pid!=n1:
                    for pfxset in random.sample(part2prefixset[pid],len(part2prefixset[pid])):
                        t1=(match_prefixes_set(sdx.pfxgrp[pfxset]))
                        sdx.part2pg[participant.id_].append(sdx.pfxgrp[pfxset][0])
                        t2=(getPred(headerFields,fieldValues,nfields))
                        t=[t1,t2]
                        tmp=t1>>t2
                        #print "SEQ: ",tmp
                        #tmp=(drop|match_prefixes_set(sdx.pfxgrp[pfxset]))
                        pdict[tmp]=fwd(participant.peers[str(pid)].participant.phys_ports[0].id_)
                    #print pdict
            """
            # outbound policies for traffic to randomly selected tier2 
            tier2=random.sample(range(n1+1,n2+1),intensityFactor*nrand) 
            for pid in tier2:
                announced=sdx.prefixes_announced['pg1'][unicode(pid)]
                pfxset=random.choice(announced)
                tmp=getPred(headerFields,fieldValues,nfields)
                tmp=(match_prefixes_set([pfxset])>>tmp)
                pdict[tmp]=fwd(participant.peers[str(pid)].participant.phys_ports[0].id_)
            """
            # inbound policies for randomly selected tier2
            
            tier2=random.sample(range(n1+1,n2+1),1) 
            if debug==True: print tier2          
            for pid in tier2:
                tmp=getPred(headerFieldInbound,fieldValues,nfields)
                if debug==True: print " content inbound pred",tmp
                assert(isinstance(tmp,sequential))
                pred=tmp.policies[0]
                if isinstance(pred,match_prefixes_set)==True:
                    pfx=(list(pred.pfxes))[0]
                    inbound[participant.id_].append(pfx)
                pdict[tmp]=fwd(participant.phys_ports[random.choice(range(len(participant.phys_ports)))].id_)
            
            
        else:
            if debug==True: print "policies for others"
            # These non-important members will write default policies
            match_ports1=no_packets
            for tmp in sdx.participant_2_port[participant.id_][participant.id_]:
                 match_ports1|=match(outport=tmp)            
            match_ports1.policies=filter(lambda x:x!=drop,match_ports1.policies)
            pdict[match_ports1]=fwd(participant.phys_ports[random.choice(range(len(participant.phys_ports)))].id_)
            
        
    
        # This is to ensure that participants have no ambiguity in its forwarding action
        # All rules are iteratively applied with if_ class of rules
        policy=getDisjointPolicies(pdict)
       
        #print policy.compile()
        if debug==True: print "Part 2 pg: ",sdx.part2pg[participant.id_],len(sdx.part2pg[participant.id_])
        if debug==True: print policy 
            
        participant.policies=policy
        participant.original_policies=participant.policies
    sdx.inbound=inbound
    # sdx.inbound

