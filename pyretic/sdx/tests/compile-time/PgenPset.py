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

def getPrefixes(sdx,n):
    pfxes={}
    for i in range(n):
        # modify later to get real IP prefixes here
        tmp='pg'+str(i+1)
        pfxes[tmp]=[tmp]
    sdx.prefixes=pfxes

def getPrefixAnnounced(k,sdx):
    return random.sample(sdx.prefixes,k)

def update_prefix2part(prefix_2_part,sdx,id):
    for pfx in sdx.prefixes_announced['pg1'][id]:
        if pfx not in prefix_2_part:
            prefix_2_part[pfx]=[]
        prefix_2_part[pfx].append(id)

def update_bgp(sdx,advertisers,nprefixes,ntot):
    if debug==True: print "Update BGP called"
    getPrefixes(sdx,nprefixes)
    n1,x=advertisers[0]
    n2,x=advertisers[1]
    n1*=(ntot)
    n2*=ntot
    
    n1=int(n1)
    #n1=1 # limiting top advertiser to 1 (hacky hack). This means that bias factor is in favor of only one top advertiser
    if n1==0:
        n1=1
    
    n2=int(n2)
    if n2==0:
        n2=1
    n2+=n1
    #print n1,n2
    N=len(sdx.prefixes.keys())
    frac=0.0
    prefix_2_part={}
    for participant in sdx.participants:
        if int(participant.id_)<=n1:
            # top advertisement prefixes
            if debug==True: print "top advertiser",participant.id_
            x,frac=advertisers[0]
        elif int(participant.id_)>n1 and int(participant.id_)<=n2:
            # middle level advertisers
            x,frac=advertisers[1]
        else:
            # low level advertisers
            x,frac=advertisers[2]
        nfrac=int(frac*N)
        if nfrac==0:
            nfrac=1
        #print nfrac
        sdx.prefixes_announced['pg1'][participant.id_]=getPrefixAnnounced(nfrac,sdx)
        update_prefix2part(prefix_2_part,sdx,participant.id_)
    if debug==True: print sdx.prefixes_announced
    sdx.prefix_2_part=prefix_2_part
    if uniformRIB==True:
        #print "uniform"
        ebgp_nh_received={}
        biasFactor=10 # probability of selecting top advertiser is 9 time that of others
        for prefix in sdx.prefixes:
            tmp=[]
            for elem in prefix_2_part[prefix]:
                #print int(elem)
                if int(elem)<=n1: 
                    # biasing the result in favor of only one top advertiser to 1 (hacky hack). This means that bias factor is in favor of only one top advertiser
                    for i in range(biasFactor*len(prefix_2_part[prefix])):
                        tmp.append(elem)                
                else:
                    tmp.append(elem)
                                
            #print "Post bias: ",tmp                   
            ebgp_nh_received[prefix]=random.choice(tmp)
        participant_to_ebgp_nh_received={}
        for participant in sdx.participants:
            participant_to_ebgp_nh_received[participant.id_]=ebgp_nh_received
        
            
    else:
        # Now assign the ebgp nh
        participant_to_ebgp_nh_received={}
        for participant in sdx.participants:
            if participant.id_ not in participant_to_ebgp_nh_received:
                participant_to_ebgp_nh_received[participant.id_]={}
            # bias the nh decision in favor of top advertisers
            biasFactor=1 # probability of selecting top advertiser is 9 time that of others
            for prefix in sdx.prefixes:  
                if prefix not in sdx.prefixes_announced['pg1'][participant.id_]:
                    tmp=[]
                    #print "Pre bias: ",prefix_2_part[prefix]
                    for elem in prefix_2_part[prefix]:
                        #print int(elem)
                        if int(elem)<=n1:
                            for i in range(biasFactor*len(prefix_2_part[prefix])):
                                tmp.append(elem)
                        
                        else:
                            tmp.append(elem)
                                        
                    #print "Post bias: ",tmp                   
                    participant_to_ebgp_nh_received[participant.id_][prefix]=random.choice(tmp)
    if debug==True: print "ebgp updated: ",participant_to_ebgp_nh_received   
    best_paths = get_bestPaths(participant_to_ebgp_nh_received)
    sdx.best_paths=best_paths
    if debug==True: print "best paths: ",best_paths
    sdx.participant_to_ebgp_nh_received=participant_to_ebgp_nh_received
    

def setPred(field,val):
    if field=='dstport':
        return match(dstport=val)
    elif field=='srcport':
        return match(srcport=val)
    elif field=='srcip':
        return match(srcip=val)
    elif field=='match_prefixes_set':
        return match_prefixes_set(val)

def getPred(headerFields,fieldValues,nfields):
    nfields=1
    #print headerFields
    fields=random.sample(headerFields,nfields)
    packet=identity
    for field in fields:
        if field in fieldValues:
            val=random.choice(fieldValues[field])
            packet=packet>>(setPred(field,val))
    packet.policies=filter(lambda x:x!=identity,packet.policies)
    return packet

def getDisjointPolicies(pdict):
    #print pdict
    #if len(pdict.keys())>0:
    k=pdict.keys()[0]
    v=pdict[k]
    pdict.pop(k,v)
    
    if k!=identity:
        #print "k:",k.policies
        if isinstance(k,sequential):
            #print "seq"
            pred=identity
            for pol in k.policies:
                #print pol,pred
                pred=intersection([pred,pol])
                #print pred
                
            #pred.policies=filter(lambda x:x!=identity,pred.policies)
        elif isinstance(k,parallel):
            #print "++"
            pred=drop
            for pol in k.policies:
                pred|=pol
            pred.policies=filter(lambda x:x!=drop,pred.policies)
        elif isinstance(k,union):
            #print "union"
            pred=drop
            for pol in k.policies:
                pred|=pol
            pred.policies=filter(lambda x:x!=drop,pred.policies)
        elif isinstance(k,intersection):
            #print "intersection"
            pred=identity
            for pol in k.policies:
                pred= pred and pol
            #pred.policies=filter(lambda x:x!=identity,pred.policies)
        
    else:
        pred=identity
    #print "pred: ",pred
    t=v    
    f=None
    #print "rem: ",pdict
    if len(pdict.keys())>=1:
        #print len(pdict.keys())
        f=getDisjointPolicies(pdict)
        #print "f: ",f
    else:
        f=drop

    return if_(pred,t,f)



def naiveCompose(sdx):
    if debug==True: print "naiveCompose called"
    compile_mode=1
    nPolicy=sdx_platform(sdx,compile_mode)

    if debug==True: print "Compile the naive policies"
    start_comp=time.time()
    nclassifier=nPolicy.compile()
    if debug==True: print nclassifier
    nRules=len(nclassifier)
    if debug==True: print nRules
    compileTime=time.time() - start_comp
    if debug==True: print  'Completed naive Compilation ',compileTime, "seconds"
    return nRules,compileTime

def lsmCompose(sdx):
    lsmPolicies=[]
    if debug==True: print "lsmCompose called"
    lowerPolicies=[]
    # take into consideration the participants with inbound policies
    # They need to be composed in parallel with other policies
    for participant in sdx.participants:
        if (isDefault(sdx,participant)==False):
            match_ports1=no_packets
            for tmp in sdx.participant_2_port[participant.id_][participant.id_]:
                 match_ports1|=match(outport=tmp)            
            match_ports1.policies=filter(lambda x:x!=drop,match_ports1.policies)
            tmp_policy=match_ports1>>participant.policies>>match_ports1
            lowerPolicies.append(tmp_policy)
            
            
    for participant in sdx.participants:

        if debug==True: print "Participant",participant.id_,participant.policies        
        # get list of all participants to which it forwards
        fwdport=extract_all_forward_actions_from_policy(participant.policies)
        
        # Remove participant's own ports from the fwdport list        
        fwdport=filter(lambda port: port not in sdx.participant_2_port[participant.id_][participant.id_],fwdport)
        tmp_policy=drop
        pdict={}
        if debug==True: print participant.policies.compile()       
        for port in fwdport:
            peer_id=sdx.port_2_participant[int(port)] # Name of fwding participant
            peer=sdx.participants_dict[peer_id] # Instance of fwding participant
            
            if debug==True: print "Seq compiling policies of part: ",participant.id_," with peer: ",peer_id
            match_ports=no_packets
            for tmp in sdx.participant_2_port[participant.id_][participant.id_]:
                 match_ports|=match(inport=tmp)            
            match_ports.policies=filter(lambda x:x!=drop,match_ports.policies)
            
            match_ports1=no_packets
            for tmp in sdx.participant_2_port[peer_id][peer_id]:
                 match_ports1|=match(outport=tmp)            
            match_ports1.policies=filter(lambda x:x!=drop,match_ports1.policies)
            tmp_policy+=(match_ports>>participant.policies>>match_ports1>>peer.policies>>match_ports1)
            
                        
        #print tmp_policy
        if debug==True: print tmp_policy.compile()
        lsmPolicies.append(tmp_policy)
    lsmPolicies+=lowerPolicies        
    lPolicy=parallel(lsmPolicies)
    if debug==True: print "Compile the lsm policies"
    start_comp=time.time()
    lclassifier=lPolicy.compile()
    if debug==True: print lclassifier
    nRules=len(lclassifier)
    if debug==True: print nRules
    compileTime=time.time() - start_comp
    if debug==True: print  'Completed lsm Compilation ',compileTime, "seconds"
    return nRules,compileTime

def removeDefault(policy):
    if isinstance(policy,if_):
        return policy.t_branch
    else:
        return policy

def simplifyInbound(selfPorts,policy):
    if isinstance(policy,if_):
        assert(isinstance(policy.t_branch,fwd))
        fwdport=policy.t_branch.outport
        if fwdport in selfPorts:
            return if_(policy.pred,policy.t_branch,simplifyInbound(selfPorts,policy.f_branch))
        else:
            return simplifyInbound(selfPorts,policy.f_branch)
    else:
        return policy
    
def isDefault(sdx,participant):
    policy=participant.policies
    assert(isinstance(policy,if_))
    assert(isinstance(policy.pred,union))
    tmp=policy.pred.policies[0]
    #assert(isinstance(tmp,match))
    
    if isinstance(tmp,match):
        if 'outport' in tmp.map:
            #print participant.id_," is default",tmp.map
            return True
            
        else:
            #print participant.id_," is non-default",tmp.map
            return False
    else:
        #print participant.id_," is not default"
        return False


def ddisjointCompose(sdx):
    parl=False
    decomposedPolicies=[]
    VNHs=sdx.VNH_2_mac.keys()
    start=time.time()
    
    decomp={}
    if parl==True:
        process=[]
        queue=[]
        qout=[]
        vnhmap={}
        i=0
        for vnh in VNHs:
            if vnh!='VNH':
                #print "Augmenting for mac: ",vnh
                affectedVNH={}
                affectedVNH[vnh]=sdx.VNH_2_mac[vnh]
                queue.append(Queue()) 
                process.append(Process(target=processVNH_MULTI, args=(sdx.participants,affectedVNH,vnh,queue[i])))
                process[i].start()
                vnhmap[i]=vnh
                #decomp[vnh]=processVNH(sdx,affectedVNH,vnh)
                i+=1
        for i in range(len(queue)):
            decomp[vnhmap[i]]=queue[i].get()
            process[i].join()
            
    else:
        for vnh in VNHs:
            if vnh!='VNH':
                #print "Augmenting for mac: ",vnh
                affectedVNH={}
                affectedVNH[vnh]=sdx.VNH_2_mac[vnh]
                decomp[vnh]=processVNH(sdx,affectedVNH,vnh)
        
                #print tmp.compile()
    augmentTime2=time.time()-start   
    #print decomposedPolicies
    """
    print decomp
    for vnh in VNHs:
        if vnh!='VNH':
            for part in sdx.participants:
                part.decomposedPolicies[vnh]=decomp[vnh][part.id_]
    """         
    nRules,compileTime=disjointDeCompose(sdx)
    
    return nRules,compileTime,augmentTime2
        
def processVNH_MULTI(participants,affectedVNH,vnh,q=None):
    start1=time.time()
    decomp={}      
    for part in participants: 
        #print "Traversing participant: ",part.id_,"'s policy"           
        #print part.id_,part.policies

        start2=time.time()
        tmp=traverse(part.policies,affectedVNH,affectedVNH)
        #print len(part.policies.__repr__()),time.time()-start2
        #part.decomposedPolicies[vnh]=tmp
        decomp[part.id_]=copyPolicy(tmp)
        
    #print "Traversing for this VNH takes time=",time.time()-start1
    if q!=None:
            q.put(decomp)
            if (debug==True): print "Put operation completed", mp.current_process()
    else:    
        return decomp 


def copyPolicy(pol):
    newpol=None
    if isinstance(pol,if_):
        newpol= if_(copyPolicy(pol.pred),copyPolicy(pol.t_branch),copyPolicy(pol.f_branch)) 
    else:
        tmp=[]
        if hasattr(pol, 'policies'):
            for plc in pol.policies:
                tmp.append(copyPolicy(plc))
            pol.policies=tmp
            newpol=pol
        else:
            if pol==drop:
                newpol=drop
            if pol==identity:
                newpol=identity
            newpol=copy.copy(pol)
    return newpol
                
            
    
    

def processVNH(sdx,affectedVNH,vnh):
    start1=time.time()
    decomp={}      
    for part in sdx.participants: 
        #print "Traversing participant: ",part.id_,"'s policy"           
        #print part.id_,part.policies

        start2=time.time()
        tmp=traverse(part.policies,affectedVNH,affectedVNH)
        #print len(part.policies.__repr__()),time.time()-start2
        part.decomposedPolicies[vnh]=tmp
        decomp[part.id_]=tmp
        
    #print "Traversing for this VNH takes time=",time.time()-start1
    return decomp  

  

def disjointDeCompose(sdx):
    disjointPolicies=[]
    lowerPolicies=[]
    fullDisjoint=True
    if debug==True: print "disjointDeCompose called",affectedVNH.values()[0]
    # take into consideration the participants with inbound policies
    # They need to be assigned lower priority than the rules matching the inport fields
    for participant in sdx.participants:
        if (isDefault(sdx,participant)==False):
            
            match_ports1=no_packets
            for tmp in sdx.participant_2_port[participant.id_][participant.id_]:
                 match_ports1|=match(outport=tmp)            
            match_ports1.policies=filter(lambda x:x!=drop,match_ports1.policies)
            selfPorts=sdx.participant_2_port[participant.id_][participant.id_]
            inboundPolicy=removeDefault(participant.policies)
            #print "After removing default: ",participant.id_,inboundPolicy
            inboundPolicy=simplifyInbound(selfPorts,inboundPolicy)
            #print "After simplification",inboundPolicy
            tmp_policy=match_ports1>>inboundPolicy>>match_ports1
            lowerPolicies.append(tmp_policy)
            #print "participant: ",participant.id_," non-default identified", tmp_policy.compile()
    
    # for now ignore the inbound policies
    #lowerPolicies=[]    
    for participant in sdx.participants:

        if debug==True: print "Recompose Participant",participant.id_,participant.policiesRecompose
        
        for vnh in participant.decomposedPolicies:
            #print "Composing policies for update#: ",ind," for participant: ",participant.id_
            fwdport=extract_all_forward_actions_from_policy(participant.decomposedPolicies[vnh])
            # Remove participant's own ports from the fwdport list        
            fwdport=filter(lambda port: port not in sdx.participant_2_port[participant.id_][participant.id_],fwdport)
            tmp_policy1=drop    
            for port in fwdport:
                peer_id=sdx.port_2_participant[int(port)] # Name of fwding participant
                peer=sdx.participants_dict[peer_id] # Instance of fwding participant
                
                if debug==True: print "2 Seq compiling policies of part: ",participant.id_," with peer: ",peer_id
                match_ports=no_packets
                for tmp in sdx.participant_2_port[participant.id_][participant.id_]:
                     match_ports|=match(inport=tmp)            
                match_ports.policies=filter(lambda x:x!=drop,match_ports.policies)
                
                match_ports1=no_packets
                for tmp in sdx.participant_2_port[peer_id][peer_id]:
                     match_ports1|=match(outport=tmp)            
                match_ports1.policies=filter(lambda x:x!=drop,match_ports1.policies)
                #print ind,newVNHs[ind],len(participant.policiesRecompose)
                tmp1=(match(dstmac=sdx.VNH_2_mac[vnh])>>match_ports>>participant.decomposedPolicies[vnh]>>match_ports1>>peer.decomposedPolicies[vnh]>>match_ports1)
                if fullDisjoint==True:
                    tmp1=drop+tmp1
                    if tmp1!=drop:
                        #print tmp1
                        #print tmp1.compile()
                        disjointPolicies.append(tmp1)
                else:
                    tmp_policy1+=tmp1
                    #print tmp_policy
            
            
                
                
            if fullDisjoint==False:
                if tmp_policy1!=drop:
                    disjointPolicies.append(tmp_policy1)   
            #print tmp_policy
            """
            if debug==True: print participant.id_,tmp_policy1.compile()
            if tmp_policy1!=drop:
                disjointPolicies.append(tmp_policy1)
        """
            
    dPolicy=disjoint(disjointPolicies,lowerPolicies)
    if debug==True: print "Compile the disjoint policies"
    start_comp=time.time()
    dclassifier=dPolicy.compile()
    if debug==True: print dclassifier
    nRules=len(dclassifier)
    
    # Save the SDX's Classifier rules
    
    
    
    if debug==True: print nRules
    compileTime=time.time() - start_comp
    if debug==True: print  'Completed Disjoint Compilation ',compileTime, "seconds"
    return nRules,compileTime     
    
def disjointDeReCompose(sdx,affectedVNHs,newVNHs):
    disjointPolicies=[]
    lowerPolicies=[]
    fullDisjoint=True
    """
    if debug==True: print "disjointDeReCompose called",affectedVNH.values()[0]
    # take into consideration the participants with inbound policies
    # They need to be assigned lower priority than the rules matching the inport fields
    for participant in sdx.participants:
        if (isDefault(sdx,participant)==False):
            
            match_ports1=no_packets
            for tmp in sdx.participant_2_port[participant.id_][participant.id_]:
                 match_ports1|=match(outport=tmp)            
            match_ports1.policies=filter(lambda x:x!=drop,match_ports1.policies)
            selfPorts=sdx.participant_2_port[participant.id_][participant.id_]
            inboundPolicy=removeDefault(participant.policies)
            #print "After removing default: ",participant.id_,inboundPolicy
            inboundPolicy=simplifyInbound(selfPorts,inboundPolicy)
            #print "After simplification",inboundPolicy
            tmp_policy=match_ports1>>inboundPolicy>>match_ports1
            lowerPolicies.append(tmp_policy)
            #print "participant: ",participant.id_," non-default identified", tmp_policy.compile()
    
    # for now ignore the inbound policies
    #lowerPolicies=[]   
    """ 
    for participant in sdx.participants:
        """
        if debug==True: print "Recompose Participant",participant.id_,participant.policiesRecompose
        
        for vnh in participant.decomposedPolicies:
            #print "Composing policies for update#: ",ind," for participant: ",participant.id_
            fwdport=extract_all_forward_actions_from_policy(participant.decomposedPolicies[vnh])
            # Remove participant's own ports from the fwdport list        
            fwdport=filter(lambda port: port not in sdx.participant_2_port[participant.id_][participant.id_],fwdport)
            tmp_policy1=drop    
            for port in fwdport:
                peer_id=sdx.port_2_participant[int(port)] # Name of fwding participant
                peer=sdx.participants_dict[peer_id] # Instance of fwding participant
                
                if debug==True: print "2 Seq compiling policies of part: ",participant.id_," with peer: ",peer_id
                match_ports=no_packets
                for tmp in sdx.participant_2_port[participant.id_][participant.id_]:
                     match_ports|=match(inport=tmp)            
                match_ports.policies=filter(lambda x:x!=drop,match_ports.policies)
                
                match_ports1=no_packets
                for tmp in sdx.participant_2_port[peer_id][peer_id]:
                     match_ports1|=match(outport=tmp)            
                match_ports1.policies=filter(lambda x:x!=drop,match_ports1.policies)
                #print ind,newVNHs[ind],len(participant.policiesRecompose)
                tmp1=(match(dstmac=sdx.VNH_2_mac[vnh])>>match_ports>>participant.decomposedPolicies[vnh]>>match_ports1>>peer.decomposedPolicies[vnh]>>match_ports1)
                if fullDisjoint==True:
                    tmp1=drop+tmp1
                    if tmp1!=drop:
                        #print tmp1
                        #print tmp1.compile()
                        disjointPolicies.append(tmp1)
                else:
                    tmp_policy1+=tmp1
                    #print tmp_policy
            
            
                
                
            if fullDisjoint==False:
                if tmp_policy1!=drop:
                    disjointPolicies.append(tmp_policy1)   
        """
        if debug==True: print "Recompose Participant",participant.id_,participant.policiesRecompose
        
        for ind in range(len(participant.policiesRecompose)):
            #print "Composing policies for update#: ",ind," for participant: ",participant.id_
            fwdport=extract_all_forward_actions_from_policy(participant.policiesRecompose[ind])
            # Remove participant's own ports from the fwdport list        
            fwdport=filter(lambda port: port not in sdx.participant_2_port[participant.id_][participant.id_],fwdport)
            tmp_policy1=drop    
            for port in fwdport:
                peer_id=sdx.port_2_participant[int(port)] # Name of fwding participant
                peer=sdx.participants_dict[peer_id] # Instance of fwding participant
                
                if debug==True: print "2 Seq compiling policies of part: ",participant.id_," with peer: ",peer_id
                match_ports=no_packets
                for tmp in sdx.participant_2_port[participant.id_][participant.id_]:
                     match_ports|=match(inport=tmp)            
                match_ports.policies=filter(lambda x:x!=drop,match_ports.policies)
                
                match_ports1=no_packets
                for tmp in sdx.participant_2_port[peer_id][peer_id]:
                     match_ports1|=match(outport=tmp)            
                match_ports1.policies=filter(lambda x:x!=drop,match_ports1.policies)
                #print ind,newVNHs[ind],len(participant.policiesRecompose)
                tmp1=(match(dstmac=newVNHs[ind].values()[0])>>match_ports>>participant.policiesRecompose[ind]>>match_ports1>>peer.policiesRecompose[ind]>>match_ports1)
                if fullDisjoint==True:
                    tmp1=drop+tmp1
                    if tmp1!=drop:
                        #print tmp1
                        #print tmp1.compile()
                        disjointPolicies.append(tmp1)
                else:
                    tmp_policy1+=tmp1
                    #print tmp_policy
            
            
                
                
            if fullDisjoint==False:
                if tmp_policy1!=drop:
                    disjointPolicies.append(tmp_policy1)   


            
    dPolicy=disjoint(disjointPolicies,lowerPolicies)
    if debug==True: print "Compile the disjoint policies"
    start_comp=time.time()
    dclassifier=dPolicy.compile()
    if debug==True: print dclassifier
    nRules=len(dclassifier)
    if debug==True: print nRules
    compileTime=time.time() - start_comp
    if debug==True: print  'Completed Disjoint Compilation ',compileTime, "seconds"
    return nRules,compileTime     
    

def disjointReCompose(sdx,affectedVNHs,newVNHs):
    disjointPolicies=[]
    lowerPolicies=[]
    fullDisjoint=True
    if debug==True: print "disjointReCompose called",affectedVNH.values()[0]
    # take into consideration the participants with inbound policies
    # They need to be assigned lower priority than the rules matching the inport fields
    for participant in sdx.participants:
        if (isDefault(sdx,participant)==False):
            
            match_ports1=no_packets
            for tmp in sdx.participant_2_port[participant.id_][participant.id_]:
                 match_ports1|=match(outport=tmp)            
            match_ports1.policies=filter(lambda x:x!=drop,match_ports1.policies)
            tmp_policy=match_ports1>>participant.policies>>match_ports1
            lowerPolicies.append(tmp_policy)
            #print "participant: ",participant.id_," non-default identified", tmp_policy.compile()
        
    for participant in sdx.participants:

        if debug==True: print "Participant",participant.id_,participant.policies
        
        # get list of all participants to which it forwards
        fwdport=extract_all_forward_actions_from_policy(participant.policies)
                
        #print list of forwardports
        #print participant.id_,": ",fwdport
        
        # Remove participant's own ports from the fwdport list        
        fwdport=filter(lambda port: port not in sdx.participant_2_port[participant.id_][participant.id_],fwdport)
        tmp_policy=drop
        if debug==True: print participant.policies.compile()       
        for port in fwdport:
            peer_id=sdx.port_2_participant[int(port)] # Name of fwding participant
            peer=sdx.participants_dict[peer_id] # Instance of fwding participant
            
            if debug==True: print "1 Seq compiling policies of part: ",participant.id_," with peer: ",peer_id
            match_ports=no_packets
            for tmp in sdx.participant_2_port[participant.id_][participant.id_]:
                 match_ports|=match(inport=tmp)            
            match_ports.policies=filter(lambda x:x!=drop,match_ports.policies)
            
            match_ports1=no_packets
            for tmp in sdx.participant_2_port[peer_id][peer_id]:
                 match_ports1|=match(outport=tmp)            
            match_ports1.policies=filter(lambda x:x!=drop,match_ports1.policies)
            #print participant.policies,peer.policies
            tmp1=(match_ports>>participant.policies>>match_ports1>>peer.policies>>match_ports1)
            if fullDisjoint==True:
                tmp1=drop+tmp1
                if tmp1!=drop:
                    disjointPolicies.append(tmp1)
            else:
                tmp_policy1+=tmp1
                #print tmp_policy
                            
            
        if fullDisjoint==False:
            if tmp_policy1!=drop:
                disjointPolicies.append(tmp_policy1)   
        #print tmp_policy
        """
        if debug==True: print participant.id_,tmp_policy1.compile()
        if tmp_policy1!=drop:
            disjointPolicies.append(tmp_policy1)
        """
        if debug==True: print "Recompose Participant",participant.id_,participant.policiesRecompose
        
        for ind in range(len(participant.policiesRecompose)):
            #print "Composing policies for update#: ",ind," for participant: ",participant.id_
            fwdport=extract_all_forward_actions_from_policy(participant.policiesRecompose[ind])
            # Remove participant's own ports from the fwdport list        
            fwdport=filter(lambda port: port not in sdx.participant_2_port[participant.id_][participant.id_],fwdport)
            tmp_policy1=drop    
            for port in fwdport:
                peer_id=sdx.port_2_participant[int(port)] # Name of fwding participant
                peer=sdx.participants_dict[peer_id] # Instance of fwding participant
                
                if debug==True: print "2 Seq compiling policies of part: ",participant.id_," with peer: ",peer_id
                match_ports=no_packets
                for tmp in sdx.participant_2_port[participant.id_][participant.id_]:
                     match_ports|=match(inport=tmp)            
                match_ports.policies=filter(lambda x:x!=drop,match_ports.policies)
                
                match_ports1=no_packets
                for tmp in sdx.participant_2_port[peer_id][peer_id]:
                     match_ports1|=match(outport=tmp)            
                match_ports1.policies=filter(lambda x:x!=drop,match_ports1.policies)
                #print ind,newVNHs[ind],len(participant.policiesRecompose)
                tmp1=(match(dstmac=newVNHs[ind].values()[0])>>match_ports>>participant.policiesRecompose[ind]>>match_ports1>>peer.policiesRecompose[ind]>>match_ports1)
                if fullDisjoint==True:
                    tmp1=drop+tmp1
                    if tmp1!=drop:
                        #print tmp1
                        #print tmp1.compile()
                        disjointPolicies.append(tmp1)
                else:
                    tmp_policy1+=tmp1
                    #print tmp_policy
            
            
                
                
            if fullDisjoint==False:
                if tmp_policy1!=drop:
                    disjointPolicies.append(tmp_policy1)   
            #print tmp_policy
            """
            if debug==True: print participant.id_,tmp_policy1.compile()
            if tmp_policy1!=drop:
                disjointPolicies.append(tmp_policy1)
        """
            
    dPolicy=disjoint(disjointPolicies,lowerPolicies)
    if debug==True: print "Compile the disjoint policies"
    start_comp=time.time()
    dclassifier=dPolicy.compile()
    if debug==True: print dclassifier
    nRules=len(dclassifier)
    if debug==True: print nRules
    compileTime=time.time() - start_comp
    if debug==True: print  'Completed Disjoint Compilation ',compileTime, "seconds"
    return nRules,compileTime     
    
        

def disjointCompose(sdx):
    fullDisjoint=True
    disjointPolicies=[]
    lowerPolicies=[]
    if debug==True: print "disjointCompose called"
    
    # take into consideration the participants with inbound policies
    # They need to be assigned lower priority than the rules matching the inport fields
    for participant in sdx.participants:
        if (isDefault(sdx,participant)==False):
            
            match_ports1=no_packets
            for tmp in sdx.participant_2_port[participant.id_][participant.id_]:
                 match_ports1|=match(outport=tmp)            
            match_ports1.policies=filter(lambda x:x!=drop,match_ports1.policies)
            tmp_policy=match_ports1>>participant.policies>>match_ports1
            lowerPolicies.append(tmp_policy)
            #print "participant: ",participant.id_," non-default identified", tmp_policy.compile()
        
        
        
    for participant in sdx.participants:

        if debug==True: print "Participant",participant.id_,participant.policies
        
        # get list of all participants to which it forwards
        fwdport=extract_all_forward_actions_from_policy(participant.policies)
                
        #print list of forwardports
        #print participant.id_,": ",fwdport
        
        # Remove participant's own ports from the fwdport list        
        fwdport=filter(lambda port: port not in sdx.participant_2_port[participant.id_][participant.id_],fwdport)
        tmp_policy=drop
        pdict={}
        if debug==True: print participant.policies.compile()       
        for port in fwdport:
            peer_id=sdx.port_2_participant[int(port)] # Name of fwding participant
            peer=sdx.participants_dict[peer_id] # Instance of fwding participant
            
            if debug==True: print "Seq compiling policies of part: ",participant.id_," with peer: ",peer_id
            match_ports=no_packets
            for tmp in sdx.participant_2_port[participant.id_][participant.id_]:
                 match_ports|=match(inport=tmp)            
            match_ports.policies=filter(lambda x:x!=drop,match_ports.policies)
            
            match_ports1=no_packets
            for tmp in sdx.participant_2_port[peer_id][peer_id]:
                 match_ports1|=match(outport=tmp)            
            match_ports1.policies=filter(lambda x:x!=drop,match_ports1.policies)
            #print participant.policies,peer.policies
            tmp1=(match_ports>>participant.policies>>match_ports1>>peer.policies>>match_ports1)
            if fullDisjoint==True:
                tmp1=drop+tmp1
                if tmp1!=drop:
                    disjointPolicies.append(tmp1)
            else:
                tmp_policy+=tmp1
                #print tmp_policy
            
            
            
        #print tmp_policy
        
        #if debug==True: print tmp_policy.compile()
        if fullDisjoint==False:
            if tmp_policy!=drop:
                disjointPolicies.append(tmp_policy)
        
            
    dPolicy=disjoint(disjointPolicies,lowerPolicies)
    if debug==True: print "Compile the disjoint policies"
    start_comp=time.time()
    dclassifier=dPolicy.compile()
    if debug==True: print dclassifier
    nRules=len(dclassifier)
    if debug==True: print nRules
    compileTime=time.time() - start_comp
    if debug==True: print  'Completed Disjoint Compilation ',compileTime, "seconds"
    return nRules,compileTime

    
def generatePolicies(sdx,participants,ntot,nmult,partTypes,frand,nfields,nval,headerFields,fieldValues):
    
    # Logic for selecting header fields
    #print "GP: ",headerFields,nfields
    headerFields=random.sample(headerFields,nfields)
    for k in fieldValues:
        fieldValues[k]=random.sample(fieldValues[k],nval)
    
    
    # Add the dstip predicate
    hfin=random.sample(headerFields,nfields)
    for k in fieldValues:
        fieldValues[k]=random.sample(fieldValues[k],nval)
    
    """
    # Currently ignoring inbound policies matching on dstip
    hfin.append('match_prefixes_set')
    vals=[]
    for k in sdx.pfxgrp.keys():
        print k
        vals.append(sdx.pfxgrp[k])
    fieldValues['match_prefixes_set']=vals
    """
    #print headerFields,hfin
    if debug==True: print fieldValues
   
    # Logic to divide the policies for top eyeballs, top content and others
    # 1: Tier 1 ISPs (5%) (1->n1)
    # 2: Tier 2 ISPs (15%) (n+1->n2)
    # 3: Top Content (5%) (n2+1->n3)
    # 4: Others (useless fellows) n3+
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

    # Logic to equally divide prefix sets announced by each Tier1 ISPs
    tmp=sdx.pfxgrp.keys()
    div=int(float(len(tmp))/nparts[0])
    pset={}
    for i in range(nparts[0]-1):
        k=i*div
        pset[i+1]=tmp[k:k+div]
    k=(nparts[0]-1)*div
    pset[nparts[0]]=tmp[k:]
    #print pset
    
    nrand=int(frand*ntot)
    if nrand==0:
        nrand=1
    #nrand=2
    intensityFactor=2 # more rules for top eyeballs and content providers    
    inbound={}
    for participant in sdx.participants:
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
                tmp=getPred(hfin,fieldValues,nfields)
                if debug==True: print "tier 1 inbound pred",tmp
                assert(isinstance(tmp,sequential))
                pred=tmp.policies[0]
                if isinstance(pred,match_prefixes_set)==True:
                    pfx=(list(pred.pfxes))[0]
                    inbound[participant.id_].append(pfx)
                pdict[tmp]=fwd(random.choice(participant.phys_ports).id_)
                
            
            #inbound policies for advertised IP prefix sets
            #This ensures that all prefix sets have at-least one rule
            #print pset[int(participant.id_)]
            """
            for pfxset in pset[int(participant.id_)]:
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
                tmp=getPred(hfin,fieldValues,nfields)
                if debug==True: print "tier 2 inbound pred",tmp.policies
                assert(isinstance(tmp,sequential))
                pred=tmp.policies[0]
                if isinstance(pred,match_prefixes_set)==True:
                    pfx=(list(pred.pfxes))[0]
                    inbound[participant.id_].append(pfx)
                pdict[tmp]=fwd(random.choice(participant.phys_ports).id_)
                        
            # outbound policies for few top eyeballs
            
            topEyeballs=random.sample(range(1,n1+1),nrand)
            for pid in topEyeballs:
                # "part: ",pid
                announced=sdx.pfxgrp.keys()
                # currently selecting only one dstip prefix set for writing specific rules
                pfxset=random.choice(announced)
                tmp=getPred(headerFields,fieldValues,nfields)
                tmp=(match_prefixes_set(sdx.pfxgrp[pfxset])>>tmp)               
                pdict[tmp]=fwd(participant.peers[str(pid)].participant.phys_ports[0].id_)
           
            
        elif int(participant.id_)>n2 and int(participant.id_)<=n3:
            if debug==True: print "policies for content providers"
            
            # outbound policies for top eyeballs
            #for pid in range(1,n1+1):
            topeyeballs=random.sample(range(1,n1+1),nrand) 
            for pid in topeyeballs:
                # "pset:",pset[pid]
                #print len(pset[pid]),pset
                for pfxset in random.sample(pset[pid],len(pset[pid])):
                    t1=(match_prefixes_set(sdx.pfxgrp[pfxset]))
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
                tmp=getPred(hfin,fieldValues,nfields)
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
        if debug==True: print policy 
            
        participant.policies=policy
        participant.original_policies=participant.policies
    sdx.inbound=inbound
    # sdx.inbound

def getPfxGroup(nprefixes,fractionGroup):
    pfxgrp={}
    ng=int(nprefixes*fractionGroup)
    #print ng
    sample=[]     
    for i in range(1,ng+1):
        tmp=ng+1-i
        tmp=tmp
        for j in range(tmp):
            sample.append(i) 
    #print sample
    for pfx in range(1,nprefixes+1):
        N=random.choice(sample)
        gname='pg'+str(N)
        if gname not in pfxgrp:
            pfxgrp[gname]=[]
        pfxgrp[gname].append(pfx)
    return pfxgrp 
    #print pfxgrp  
    
def traverse(policy,affectedVNH,newVNH):
    #print "Called for : ",policy
    if isinstance(policy,intersection):
        #print policy
        tmp=intersection(map(lambda p: traverse(p,affectedVNH,newVNH), policy.policies))
        flag=False
        
        #print tmp.policies
        for pol in tmp.policies:            
            if isinstance(pol,match):
                #if 'dstmac' in pol.map:
                flag=True
            if isinstance(pol,union) or isinstance(pol,parallel) or isinstance(pol,intersection):
                flag=True
        if flag==True:
            #print "App match pol: ",tmp
            tmp.policies=filter(lambda p:p!=identity,tmp.policies)
            #print "App post filter: ",tmp
            if drop not in tmp.policies:
                return tmp
            else:
                return union([])
        else:
            return union([])

    
    elif isinstance(policy, union):
        #print "init",policy
        
        tmp=union(map(lambda p: traverse(p,affectedVNH,newVNH), policy.policies))
        flag=False
        #print policy.policies
        for pol in tmp.policies:            
            if isinstance(pol,match):
                #if 'dstmac' in pol.map:
                flag=True
            if isinstance(pol,union) or isinstance(pol,parallel) or isinstance(pol,intersection):
                flag=True
        if flag==True:
            #print "App match pol: ",tmp
            tmp.policies=filter(lambda p:p!=drop,tmp.policies)
            #print "App post filter: ",tmp
            return tmp
        else:
            return union([])

    elif isinstance(policy, parallel):
        #print "++ before",policy.policies
        tmp=parallel(map(lambda p: traverse(p,affectedVNH,newVNH), policy.policies))
        tmp.policies=filter(lambda p:p!=drop,tmp.policies) 
        #print "++ ater",tmp.policies
        flag=False
        #print policy.policies
        for pol in tmp.policies:            
            if isinstance(pol,match):
                if 'dstmac' in pol.map:
                    flag=True
            elif isinstance(pol,sequential):
                flag=True

        if flag==True:
            #print "++App match pol: ",tmp
            tmp.policies=filter(lambda p:p!=drop,tmp.policies)
            #print "++App post filter: ",tmp
            return tmp
        else:
            return union([])
               
        return tmp
    
    elif isinstance(policy, sequential):
        tmp=sequential(map(lambda p: traverse(p,affectedVNH,newVNH), policy.policies))
        #tmp.policies=filter(lambda p:p!=drop,tmp.policies)
        if drop in tmp.policies:
            return drop
        else:
            return tmp
    elif isinstance(policy, if_):
        #if debug==True: print policy
        pred=traverse(policy.pred,affectedVNH,newVNH)
        t=traverse(policy.t_branch,affectedVNH,newVNH)                  
        f=traverse(policy.f_branch,affectedVNH,newVNH)
        if pred==drop:
            return f
        else:
            return if_(traverse(policy.pred,affectedVNH,newVNH),
                   traverse(policy.t_branch,affectedVNH,newVNH),
                   traverse(policy.f_branch,affectedVNH,newVNH))
    else:
        if isinstance(policy, match):
            if 'dstmac' in policy.map:
                #print policy.map['dstmac']
                if policy.map['dstmac']==affectedVNH.values()[0]:
                    #print "Affected mac found"
                    return match(dstmac=newVNH.values()[0])
                else:
                    return drop
            else:
                return policy
        else:
            return policy
    

def main(argv):
    # define the parameters
    ntot=200 # total number of participants
    fmult=0.05  # fraction of participants with multiple ports
    nmult=int(ntot*fmult)
    nports=2 # number of ports for the participants with multiple ports 
    nprefixes=100 # total # of prefixes
    fractionGroup=0.1 # fraction of prefix groups wrt total prefixes
    
    #Np=100 #total number of prefixes
    advertisers=[(0.1,1),(0.05,0.20),(0.85,0.01)]
    partTypes=[0.15,0.05,0.05,0.75]
    frand=0.025
    nfields=1
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
    print nRules,compileTime,augmentTime1,float(augmentTime2)/len(sdx.VNH_2_IP.keys())
    
    """
    compile_Policies(participants)
    start=time.time()
    nRules,compileTime=disjointCompose(sdx)
    print nRules,compileTime
    
    # Get Compiler's cache size
    s1=total_size(policy_parl,verbose=False)
    s2=total_size(policy_seq,verbose=False)
    s3=total_size(disjoint_cache,verbose=False)
    cachSize=s1+s2+s3
    print "Cache sizes: ",cachSize
    """
    # Process BGP Updates
    updateEval=True    
    if updateEval==True:        
        nUpdates=1
        biasfactor=10
        nRules1,compileTime1=addVNH(sdx,nUpdates,biasfactor,advertisers,ntot)
        
        
    

def addVNH(sdx,nUpdates,biasfactor,advertisers,ntot):
    affectedVNHs=[]
    newMacs=[]
    print "# of updates: ",nUpdates
    for ind in range(nUpdates):
        # find the prefix to send update for
        #print "Finding the right prefix"
        upPfx,pset_orig=getUpdatePfx(sdx) 
        #print upPfx           
        bp=sdx.best_paths[unicode(1)]
        pool=[]
        removed=0
        for peer in bp:
            if upPfx in bp[peer]:
                pool=sdx.prefix_2_part[upPfx]
                removed=unicode(peer)
                pool.remove(unicode(peer))
        # Ensure that there is choice in case of withdraw message
        assert(len(pool)!=0)
        
        frac,x=advertisers[0]
        n1=int(frac*ntot)
        if n1==0:
            n1=1
        tmp=[]
        for elem in pool:
            if int(elem)<=n1:
                for i in range(biasfactor*len(pool)):
                    tmp.append(elem)
            else:
                tmp.append(elem)
        nh=random.choice(tmp)
        sdx.prefix_2_part[upPfx].append(removed)
        #print "new NH: ",(nh)," for prefix from the group: ",upPfx
        
        # Find the affected VNH
        affectedVNH={}
        for vnh in sdx.VNH_2_pfx:
            if upPfx in sdx.VNH_2_pfx[vnh]:
                #print vnh,sdx.VNH_2_mac[vnh]
                affectedVNH[vnh]=sdx.VNH_2_mac[vnh]
        
        # Get a new VNH
        count=len(sdx.lcs_old)+1+ind
        vname='VNH'+str((count))
        newMac={}
        newMac[vname] = MAC(str(EUI(int(EUI(VNH_2_mac['VNH']))+count)))
        
        newMacs.append(newMac)
        affectedVNHs.append(affectedVNH)
        
        for part in sdx.participants:
            if ind==0:
                part.policiesRecompose=[]
            #print part.id_,part.decomposedPolicies[affectedVNH.keys()[0]]
            tmp=traverse(part.decomposedPolicies[affectedVNH.keys()[0]],affectedVNH,newMac)
            #print part.id_,tmp
            part.policiesRecompose.append(tmp)
            #print tmp.compile()
    #print newMacs  
    nRules,compileTime=disjointDeReCompose(sdx,affectedVNHs,newMacs)
    print nRules,compileTime
    return nRules,compileTime
    

def processBGPUpdateBurst(sdx,nUpdates,biasfactor,advertisers,ntot):
    affectedVNHs=[]
    newMacs=[]
    print "# of updates: ",nUpdates
    for ind in range(nUpdates):
        # find the prefix to send update for
        #print "Finding the right prefix"
        upPfx,pset_orig=getUpdatePfx(sdx) 
        #print upPfx           
        bp=sdx.best_paths[unicode(1)]
        pool=[]
        removed=0
        for peer in bp:
            if upPfx in bp[peer]:
                pool=sdx.prefix_2_part[upPfx]
                removed=unicode(peer)
                pool.remove(unicode(peer))
        # Ensure that there is choice in case of withdraw message
        assert(len(pool)!=0)
        
        frac,x=advertisers[0]
        n1=int(frac*ntot)
        if n1==0:
            n1=1
        tmp=[]
        for elem in pool:
            if int(elem)<=n1:
                for i in range(biasfactor*len(pool)):
                    tmp.append(elem)
            else:
                tmp.append(elem)
        nh=random.choice(tmp)
        sdx.prefix_2_part[upPfx].append(removed)
        #print "new NH: ",(nh)," for prefix from the group: ",upPfx
        
        # Find the affected VNH
        affectedVNH={}
        for vnh in sdx.VNH_2_pfx:
            if upPfx in sdx.VNH_2_pfx[vnh]:
                #print vnh,sdx.VNH_2_mac[vnh]
                affectedVNH[vnh]=sdx.VNH_2_mac[vnh]
        
        # Get a new VNH
        count=len(sdx.lcs_old)+1+ind
        vname='VNH'+str((count))
        newMac={}
        newMac[vname] = MAC(str(EUI(int(EUI(VNH_2_mac['VNH']))+count)))
        
        newMacs.append(newMac)
        affectedVNHs.append(affectedVNH)
        
        for part in sdx.participants:
            if ind==0:
                part.policiesRecompose=[]
            #print part.id_,part.policies
            tmp=traverse(sdx,part.policies,affectedVNH,newMac)
            #print part.id_,tmp
            part.policiesRecompose.append(tmp)
            #print tmp.compile()
    #print newMacs  
    nRules,compileTime=disjointReCompose(sdx,affectedVNHs,newMacs)
    print nRules,compileTime
    return nRules,compileTime
    
def getUpdatePfx(sdx):
    """
    tmp={}
    mlen=0
    for elem in sdx.lcs_old:
        l=len(elem)
        tmp[l]=elem
        if l>mlen:
            mlen=l
    #print mlen,tmp[mlen]
    upPfx=random.choice(list(tmp[mlen]))
    return upPfx,tmp[mlen]
    """
    # changed as we are now dealing with prefix groups rather than actual prefixes
    return random.choice(sdx.pfxgrp.keys()),[]
  
def getFwd(sdx):
    p2f={}
    for part in sdx.participants:
        fwdports=extract_all_forward_actions_from_policy(part.policies)
        fwdports=filter(lambda port: port not in sdx.participant_2_port[part.id_][part.id_],fwdports)
        p2f[part.id_]=fwdports
    return p2f
   
def findPfxgroup(aPrefix,pfx_2_grp):
    for k,v in pfx_2_grp.iteritems():
        if aPrefix in v:
            return k
    

def generate_pfxgrpmappings(sdx,nprefixes,Np):
    pgrp=sdx.prefixes.keys()
    sample=[]
    for i in range(1,len(pgrp)+1):
        
        tmp=i*i*i # cubic distribution for now
        for j in range(tmp):
            sample.append(pgrp[i-1])
    #print sample
    pfx_2_grp={}
    for i in range(1,Np+1):
        tmp=random.choice(sample)
        if tmp not in pfx_2_grp:
            pfx_2_grp[tmp]=[]
        pfx_2_grp[tmp].append(i)
        pfx_2_grp[tmp].append(i)
    #print pfx_2_grp 
    for k in pfx_2_grp:
        pfx_2_grp[k]=set(pfx_2_grp[k])
        
    
    #print pfx_2_grp    
    return pfx_2_grp     
    
    
        
if __name__ == '__main__':
    #cProfile.run('main()', 'restats')
    sys.setrecursionlimit(100000)
    
    main(sys.argv)