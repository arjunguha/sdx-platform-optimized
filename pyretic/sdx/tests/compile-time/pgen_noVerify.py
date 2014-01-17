#############################################
# author: Arpit Gupta (glex.qsd@gmail.com)  #
#############################################

from common import *
import sys,json
verify=False
debug=False

headerFields=['dstport','srcport','srcip']
fieldValues={'dstport':range(1,101),'srcport':range(1,101),
             'srcip':list(IPNetwork('172.0.0.1/26'))}

def getPrefixes(sdx,n):
    pfxes={}
    for i in range(n):
        # modify later to get real IP prefixes here
        pfxes['p'+str(i+1)]=''
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
    n1=1 # limiting top advertiser to 1 (hacky hack)
    if n1==0:
        n1=1
    
    n2=int(n2)
    if n2==0:
        n2=1
    n2+=n1
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
        sdx.prefixes_announced['pg1'][participant.id_]=getPrefixAnnounced(nfrac,sdx)
        update_prefix2part(prefix_2_part,sdx,participant.id_)
    if debug==True: print sdx.prefixes_announced
    sdx.prefix_2_part=prefix_2_part
    # Now assign the ebgp nh
    participant_to_ebgp_nh_received={}
    for participant in sdx.participants:
        if participant.id_ not in participant_to_ebgp_nh_received:
            participant_to_ebgp_nh_received[participant.id_]={}
        # bias the nh decision in favor of top advertisers
        biasFactor=9 # probability of selecting top advertiser is 9 time that of others
        for prefix in sdx.prefixes:  
            if prefix not in sdx.prefixes_announced['pg1'][participant.id_]:
                tmp=[]
                #print "Pre bias: ",prefix_2_part[prefix]
                for elem in prefix_2_part[prefix]:
                    #print int(elem)
                    if int(elem)<=n1:
                        for i in range(biasFactor):
                            tmp.append(elem)
                    
                    else:
                        tmp.append(elem)
                                    
                #print "Post bias: ",tmp                   
                participant_to_ebgp_nh_received[participant.id_][prefix]=random.choice(tmp)
    if debug==True: print "ebgp updated: ",participant_to_ebgp_nh_received   
    best_paths = get_bestPaths(participant_to_ebgp_nh_received)
    if debug==True: print best_paths
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
    k=pdict.keys()[0]
    v=pdict[k]
    pdict.pop(k,v)
    pred=drop
    if k!=identity:
        for pol in k.policies:
            pred|=pol
        pred.policies=filter(lambda x:x!=drop,pred.policies)
    else:
        pred=identity
    t=v    
    f=None
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

    
    

def disjointCompose(sdx):
    disjointPolicies=[]
    if debug==True: print "disjointCompose called"
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
            tmp_policy+=(match_ports>>participant.policies>>match_ports1>>peer.policies>>match_ports1)
            #print tmp_policy
            
            
            
        #print tmp_policy
        if debug==True: print tmp_policy.compile()
        disjointPolicies.append(tmp_policy)
            
    dPolicy=disjoint(disjointPolicies)
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
    headerFields=random.sample(headerFields,nfields)
    for k in fieldValues:
        fieldValues[k]=random.sample(fieldValues[k],nval)
    # Add the dstip predicate
    headerFields.append('match_prefixes_set')
    vals=[]
    for k in sdx.prefixes.keys():
        #print k
        vals.append(set([str(k)]))
    fieldValues['match_prefixes_set']=vals
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
    tmp=sdx.prefixes.keys()
    div=int(float(len(tmp))/nparts[0])
    pset={}
    for i in range(nparts[0]-1):
        k=i*div
        pset[i+1]=tmp[k:k+div]
    k=(nparts[0]-1)*div
    pset[nparts[0]]=tmp[k:]
    
    nrand=int(frand*ntot)
    if nrand==0:
        nrand=1
    intensityFactor=1 # more rules for top eyeballs and content providers    
     
    for participant in sdx.participants:
        policy=drop
        pdict={}

        if debug==True: print 'participant: ',participant.id_,sdx.participant_2_port[participant.id_][participant.id_]
        
        if int(participant.id_)<=n1:
            if debug==True: print "policies for Tier1 ISPs"
            
            #inbound policies for advertised IP prefix sets
            #This ensures that all prefix sets have at-least one rule
            #print pset[int(participant.id_)]
            for pfxset in pset[int(participant.id_)]:
                pdict[drop|(match_prefixes_set([pfxset]))]=fwd(random.choice(participant.phys_ports).id_)
                
            # inbound policies for traffic coming from top content folks            
            for pid in range(n2+1,n3+1):
                pdict[getPred(headerFields,fieldValues,nfields)]=fwd(random.choice(participant.phys_ports).id_)
                       
                        
        elif int(participant.id_)>n1 and int(participant.id_)<=n2:
            if debug==True: print "policies for Tier 2 ISPs"
            # inbound policies for few top content participants
            topContent=random.sample(range(n2+1,n3+1),nrand)
            for pid in topContent:
                pdict[getPred(headerFields,fieldValues,nfields)]=fwd(random.choice(participant.phys_ports).id_)
                        
            # outbound policies for few top eyeballs
            topEyeballs=random.sample(range(1,n1+1),nrand)
            for pid in topEyeballs:
                pdict[getPred(headerFields,fieldValues,nfields)]=fwd(participant.peers[str(pid)].participant.phys_ports[0].id_)
           
            
        elif int(participant.id_)>n2 and int(participant.id_)<=n3:
            if debug==True: print "policies for content providers"
            
            # outbound policies for top eyeballs
            for pid in range(1,n1+1):
                pdict[getPred(headerFields,fieldValues,nfields)]=fwd(participant.peers[str(pid)].participant.phys_ports[0].id_)
            
            # outbound policies for traffic to randomly selected tier2 
            tier2=random.sample(range(n1+1,n2+1),intensityFactor*nrand) 
            for pid in tier2:
                pdict[getPred(headerFields,fieldValues,nfields)]=fwd(participant.peers[str(pid)].participant.phys_ports[0].id_)

            # inbound policies for randomly selected others 
            tier2=random.sample(range(n1+1,n2+1),intensityFactor*nrand) 
            if debug==True: print tier2          
            for pid in tier2:
                 pdict[getPred(headerFields,fieldValues,nfields)]=fwd(participant.phys_ports[random.choice(range(len(participant.phys_ports)))].id_)
            
            
        else:
            if debug==True: print "policies for others"
            # These non-important members will write default policies
            pdict[identity]=fwd(participant.phys_ports[random.choice(range(len(participant.phys_ports)))].id_)
            
            
        # This is to ensure that participants have no ambiguity in its forwarding action
        # All rules are iteratively applied with if_ class of rules
        policy=getDisjointPolicies(pdict)
        #print policy.compile()
        if debug==True: print policy 
            
        participant.policies=policy
        participant.original_policies=participant.policies
            

def main(argv):
    # define the parameters
    ntot=10 # total number of participants
    fmult=0.2  # fraction of participants with multiple ports
    nmult=int(ntot*fmult)
    nports=2 # number of ports for the participants with multiple ports 
    nprefixes=5
    advertisers=[(0.05,1),(0.15,0.20),(0.80,0.01)]
    partTypes=[0.05,0.15,0.05,0.75]
    frand=0.025
    nfields=0
    nval=5
    
    sdx_participants=generate_sdxglobal(ntot,nmult,nports) 
       
    (sdx,participants) = sdx_parse_config('sdx_global.cfg')
    
    update_paramters(sdx,ntot,nports)
    
    update_bgp(sdx,advertisers,nprefixes,ntot)    
    
    generatePolicies(sdx,participants,ntot,nmult,partTypes,frand,nfields,nval,headerFields,fieldValues)
    
    """
    vnh_assignment(sdx,participants)
    
    compile_Policies(participants)
    
    nRules,compileTime=disjointCompose(sdx)
    print nRules,compileTime
    """


    
    
        
if __name__ == '__main__':
    #cProfile.run('main()', 'restats')
    
    
    main(sys.argv)