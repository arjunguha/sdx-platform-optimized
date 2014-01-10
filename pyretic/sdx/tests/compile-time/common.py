#############################################              #
# author: Arpit Gupta (glex.qsd@gmail.com)  #
#############################################
"""
common functionalities for compile time experiments
"""

import os,json,sys,random
from netaddr import *
import cProfile
import pstats

## Pyretic-specific imports
from pyretic.lib.corelib import *
from pyretic.lib.std import *

## SDX-specific imports
from pyretic.sdx.lib.common import *
from pyretic.sdx.lib.core import *
from pyretic.sdx.lib.vnhAssignment import *

iplist=list(IPNetwork('182.0.0.1/16'))
macinit='A1:A1:00:00:00:00'

def compare_policies(policy1,policy2,flag=[]):
    if isinstance(policy1, parallel):
        if isinstance(policy2, parallel)and (len(policy1.policies)==len(policy2.policies)):
            for p1,p2 in zip(policy1.policies,policy2.policies):
                compare_policies(p1,p2,flag)
        else:
            flag.append(False)
            return False
            
    elif isinstance(policy1,sequential):
        if isinstance(policy2, sequential)and (len(policy1.policies)==len(policy2.policies)):
            for p1,p2 in zip(policy1.policies,policy2.policies):
                compare_policies(p1,p2,flag)
        else:                    
            flag.append(False)
            return False
            
    elif isinstance(policy1, if_):
        if isinstance(policy2, if_):
            compare_policies(policy1.pred,policy2.pred,flag)
            compare_policies(policy1.t_branch,policy2.t_branch,flag)
            compare_policies(policy1.f_branch,policy2.f_branch,flag)
        else:
            flag.append(False)
            return False
    
    elif isinstance(policy1, fwd):   
        if isinstance(policy2, fwd):
            if policy2.outport==policy1.outport:
                flag.append(True)
                return True
        flag.append(False)
        return False
    
    elif isinstance(policy1, modify):   
        if isinstance(policy2, modify):
            if policy2.map==policy1.map:
                flag.append(True)
                return True
        flag.append(False)
        return False
     
    elif isinstance(policy1,match):   
        if policy1==policy2:
            flag.append(True)
            return True
        #print "false flag set for match"
        flag.append(False) 
        return False 
    #print flag
    if False in flag:
        return False
    else:
        return True

def generate_sdxglobal(ntot,nin):
    sdx_participants={}
    for ind in range(1,ntot+1):
        peers=[]
        for i in range(1,ntot+1):
            if i!=ind:
                peers.append(str(i))
        ports=[]
        count =ind
        ip,mac=str(iplist[count]),str(EUI(int(EUI(macinit))+count))
        ports.append({'Id':count,'MAC':mac,'IP':ip})
        if ind<=nin:         
            for i in range(2):
                count=(ind-1)*2+i+1+ntot
                ip,mac=str(iplist[count]),str(EUI(int(EUI(macinit))+count))
                ports.append({'Id':count,'MAC':mac,'IP':ip})                   
        
        
        sdx_participants[ind]={'Ports':ports,'Peers':peers}
        with open('sdx_global.cfg', 'w') as outfile:
            json.dump(sdx_participants,outfile,ensure_ascii=True)
    return sdx_participants

def update_paramters(sdx,ntot,nin):
    participant_2_port={}
    port_2_participant={}
    prefixes_announced={}
    participant_to_ebgp_nh_received={}
    prefixes_announced['pg1']={}
    peer_groups={'pg1':range(1,ntot+1)}
    participants_dict={}
    for participant in sdx.participants:
        participants_dict[participant.id_]=participant
        if int(participant.id_)<=nin:
            prefixes_announced['pg1'][participant.id_]=sdx.prefixes.keys()
        else:
            participant_to_ebgp_nh_received[participant.id_]={}
            for pfx in sdx.prefixes.keys():
                participant_to_ebgp_nh_received[participant.id_][pfx]=random.randint(1,nin)
        participant_2_port[participant.id_]={}
        participant_2_port[participant.id_][participant.id_]=[participant.phys_ports[i].id_ 
                                                              for i in range(len(participant.phys_ports))]
        for phyport in participant.phys_ports:
            port_2_participant[phyport.id_]=participant.id_
        for peer in participant.peers:
            participant_2_port[participant.id_][peer]=[participant.peers[peer].participant.phys_ports[0].id_]
    print 'participant_2_port: ',participant_2_port
    print 'port_2_participant: ',port_2_participant
    print 'prefixes_announced: ',prefixes_announced
    print 'participant_to_ebgp_nh_received: ',participant_to_ebgp_nh_received
    # Update SDX's data structure
    sdx.participants_dict=participants_dict
    sdx.participant_2_port=participant_2_port
    sdx.port_2_participant=port_2_participant
    sdx.prefixes_announced=prefixes_announced
    sdx.participant_to_ebgp_nh_received=participant_to_ebgp_nh_received


def generate_policies(sdx,participants,ntot,nin):
    for participant in sdx.participants:
        print participant.id_
        if int(participant.id_)<=nin:
            print "inbound policies"
            policy=((match(dstport=80) >> sdx.fwd(participant.phys_ports[2]))+
                    (match(dstport=22) >> sdx.fwd(participant.phys_ports[1]))
                   )
        else:
            print "outbound policies"
            port_init=25
            policy=(match(srcport=port_init) >> sdx.fwd(participant.peers['1']))
            
            """
            for peer in range(0,nin-1):
                print peer
                policy=(match(dstport=port_init+(peer+1)*10) >> sdx.fwd(participant.peers[peer+1]))+policy
            """
        #print "output policy: ",policy
        participant.policies=policy
        participant.original_policies=participant.policies
        participant.policies=pre_VNH(participant.policies,sdx,participant.id_,participant)
        #print "After PreVNH"
        #print participant.policies
    
    vnh_assignment(sdx,participants)
    classifier=[]
    
    for participant_name in participants:
        print participant_name
        participants[participant_name].policies=post_VNH(participants[participant_name].policies,
                                                         sdx,participant_name)   
        #print participants[participant_name].policies    
    compile_Policies(participants)