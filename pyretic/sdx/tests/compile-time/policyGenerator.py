#############################################
# author: Arpit Gupta (glex.qsd@gmail.com)  #
#############################################

from common import *
import sys,json

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
    print "Update BGP called"
    getPrefixes(sdx,nprefixes)
    n1,x=advertisers[0]
    n2,x=advertisers[1]
    n1*=(ntot)
    n2*=ntot
    
    n1=int(n1)
    if n1==0:
        n1=1
    
    n2=int(n2)
    if n2==0:
        n2=1
    n2+=n1
    print n2,n1
    N=len(sdx.prefixes.keys())
    frac=0.0
    prefix_2_part={}
    for participant in sdx.participants:
        if int(participant.id_)<=n1:
            # top advertisement prefixes
            print "top advertiser",participant.id_
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
    print sdx.prefixes_announced
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
                    """
                    else:
                        tmp.append(elem)
                    """                
                #print "Post bias: ",tmp                   
                participant_to_ebgp_nh_received[participant.id_][prefix]=random.choice(tmp)
    print "ebgp updated: "        
    sdx.participant_to_ebgp_nh_received=participant_to_ebgp_nh_received

def setPred(field,val):
    if field=='dstport':
        return match(dstport=val)
    elif field=='srcport':
        return match(srcport=val)
    elif field=='srcip':
        return match(srcip=val)
    

def getPred(headerFields,fieldValues,nfields):
    nfields=1
    fields=random.sample(headerFields,nfields)
    packet=identity
    for field in fields:
        if field in fieldValues:
            val=random.choice(fieldValues[field])
            packet=packet>>(setPred(field,val))
    packet.policies=filter(lambda x:x!=identity,packet.policies)
    return packet
    
def generatePolicies(sdx,participants,ntot,nmult,partTypes,frand,nfields,nval,headerFields,fieldValues):
    # Logic for selecting header fields


    headerFields=random.sample(headerFields,nfields)
    for k in fieldValues:
        fieldValues[k]=random.sample(fieldValues[k],nval)
    
    # Logic to divide the policies for top eyeballs, top content and rest players
    n1=int(partTypes[0]*ntot)
    n2=int(partTypes[1]*ntot)
    n2+=n1
    nrand=int(frand*ntot)
    if nrand==0:
        nrand=1
    intensityFactor=4 # more rules for top eyeballs and content providers    
     
    for participant in sdx.participants:
        policy=drop
        print 'participant: ',participant.id_,sdx.participant_2_port[participant.id_][participant.id_]
        if int(participant.id_)<=n1:
            print "policies for Tier1 ISPs"
            
            # inbound policies for traffic coming from top content folks            
            for pid in range(n1+1,n2+1):
                policy+=(getPred(headerFields,fieldValues,nfields)>>
                         fwd(random.choice(participant.phys_ports).id_))
                        
            # outbound policies for traffic to randomly selected others 
            others=random.sample(range(n2,ntot+1),intensityFactor*nrand) 
            print others
            for pid in others:
                policy+=(getPred(headerFields,fieldValues,nfields)
                         >>fwd(participant.peers[str(pid)].participant.phys_ports[0].id_))
            participant.policies=policy
            policy.policies=filter(lambda x:x!=drop,policy.policies)
            print policy             

        elif int(participant.id_)>n1 and int(participant.id_)<=n2:
            print "policies for content providers"
            # outbound policies for top prefix advertisers
            print range(1,n1+1)
            for pid in range(1,n1+1):
                policy+=(getPred(headerFields,fieldValues,nfields)
                         >>fwd(participant.peers[str(pid)].participant.phys_ports[0].id_))
            
            # inbound policies for randomly selected others 
            others=random.sample(range(n2+1,ntot+1),intensityFactor*nrand) 
            print others          
            for pid in others:
                 policy+=(getPred(headerFields,fieldValues,nfields)
                          >>fwd(participant.phys_ports[
                        random.choice(range(len(participant.phys_ports)))].id_))
            policy.policies=filter(lambda x:x!=drop,policy.policies)
            print policy

        else:
            print "policies for others"
            # These non-important members will write policies for important ones 
            # outbound policies to fraction of top prefix advertiser
            peers=participant.peers.keys()
            others=random.sample(range(1,n1+1),nrand) 
            print others
            for pid in others:
                policy+=(getPred(headerFields,fieldValues,nfields)
                         >>fwd(participant.peers[str(pid)].participant.phys_ports[0].id_))
                
            # inbound policies for traffic coming from fraction of top content providers 
            others=random.sample(range(n2+1,ntot+1),nrand) 
            
            for pid in others:
                policy+=(getPred(headerFields,fieldValues,nfields)
                         >>fwd(participant.phys_ports[
                        random.choice(range(len(participant.phys_ports)))].id_))
            policy.policies=filter(lambda x:x!=drop,policy.policies)
            print policy
            
        participant.policies=policy
        participant.original_policies=participant.policies
    
    vnh_assignment(sdx,participants)
    compile_Policies(participants)
    
            

def main(argv):
    # define the parameters
    ntot=20 # total number of participants
    fmult=0.2  # fraction of participants with multiple ports
    nmult=int(ntot*fmult)
    nports=2 # number of ports for the participants with multiple ports 
    nprefixes=50
    advertisers=[(0.05,1),(0.15,0.20),(0.80,0.01)]
    sdx_participants=generate_sdxglobal(ntot,nmult,nports)    
    (sdx,participants) = sdx_parse_config('sdx_global.cfg')
    print participants
    #getPrefixes(sdx,nprefixes)
    update_paramters(sdx,ntot,nports)
    update_bgp(sdx,advertisers,nprefixes,ntot)
    partTypes=[0.05,0.05,0.9]
    frand=0.025
    headerFields=['dstport','srcport','srcip']
    fieldValues={'dstport':range(1,101),'srcport':range(1,101),
                 'srcip':list(IPNetwork('172.0.0.1/26'))}
    nfields=3
    nval=50
    generatePolicies(sdx,participants,ntot,nmult,partTypes,frand,nfields,nval,headerFields,fieldValues)

if __name__ == '__main__':
    #cProfile.run('main()', 'restats')
    main(sys.argv)