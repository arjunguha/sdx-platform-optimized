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
    n1*=ntot
    n2*=ntot
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
        sdx.prefixes_announced['pg1'][participant.id_]=getPrefixAnnounced(int(frac*N),sdx)
        update_prefix2part(prefix_2_part,sdx,participant.id_)
    print sdx.prefixes_announced
    sdx.prefix_2_part=prefix_2_part
    # Now assign the ebgp nh
    participant_to_ebgp_nh_received={}
    for participant in sdx.participants:
        if participant.id_ not in participant_to_ebgp_nh_received:
            participant_to_ebgp_nh_received[participant.id_]={}
        for prefix in sdx.prefixes:            
            participant_to_ebgp_nh_received[participant.id_][prefix]=random.choice(prefix_2_part[prefix])
    print "ebgp updated: "        
    sdx.participant_to_ebgp_nh_received=participant_to_ebgp_nh_received
    
def generatePolicies(sdx,ntot,nmult,partTypes):
    n1=partTypes[0]*ntot
    n2=partTypes[1]*ntot
    n2+=n1
    for participant in sdx.participants:
        if int(participant.id_)<=n1:
            print "policies for Tier1 ISPs"
            

        elif int(participant.id_)>n1 and int(participant.id_)<=n2:
            print "policies for content providers"

        else:
            print "policies for others"

    
            

def main(argv):
    # define the parameters
    ntot=20 # total number of participants
    fmult=0.2  # fraction of participants with multiple ports
    nmult=int(ntot*fmult)
    nports=2 # number of ports for the participants with multiple ports 
    nprefixes=100
    advertisers=[(0.05,1),(0.15,0.20),(0.80,0.01)]
    sdx_participants=generate_sdxglobal(ntot,nmult,nports)    
    (sdx,participants) = sdx_parse_config('sdx_global.cfg')
    #getPrefixes(sdx,nprefixes)
    update_paramters(sdx,ntot,nports)
    update_bgp(sdx,advertisers,nprefixes,ntot)
    partTypes=[0.05,0.05,0.9]
    generatePolicies(sdx,ntot,nmult,partTypes)

if __name__ == '__main__':
    #cProfile.run('main()', 'restats')
    main(sys.argv)