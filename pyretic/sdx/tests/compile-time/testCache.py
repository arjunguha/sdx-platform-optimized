#############################################
# Experiment to evaluate the compilation    #
# times for 100 participants                #
# author: Arpit Gupta (glex.qsd@gmail.com)  #
#############################################
"""
ntot participants
nin of them advertising p1,p2,p3,p4,p5,p6 with inbound policies
ntot-nin of them with outbound policies
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
        print participant.policies
    
    vnh_assignment(sdx,participants)
    classifier=[]
    
    for participant_name in participants:
        print participant_name
        #participants[participant_name].policies=post_VNH(participants[participant_name].policies,
        #                                                 sdx,participant_name)   
        print participants[participant_name].policies    
    compile_Policies(participants)
    

def compileParallel(sdx):
    classifier_dict={}
    aggr_rules=[]
    for participant in sdx.participants:
        print participant.id_
        fwdport=extract_all_forward_actions_from_policy(participant.policies)
        print participant.id_,": ",fwdport
        print sdx.participant_2_port
        fwdport=filter(lambda port: port not in sdx.participant_2_port[participant.id_][participant.id_],fwdport)
        for port in fwdport:
            peer_id=sdx.port_2_participant[int(port)]
            peer=sdx.participants_dict[peer_id]
            outport_of_2=sdx.participant_2_port[participant.id_][peer_id][0]
            print "Seq compiling policies of part: ",participant.id_," with peer: ",peer_id, " outport: ",outport_of_2            
            #tmp_policy=participant.policies>>if_(match(outport=outport_of_2),peer.policies,identity)
            tmp_policy=participant.policies>>peer.policies
            tmp_classifier=tmp_policy.compile()
            classifier_dict[(participant.id_,peer_id)]=tmp_classifier.rules
    print "Classifier Dict: ",classifier_dict
    for k,v in classifier_dict.iteritems():
        aggr_rules+=v
    print "aggregate rules: ",aggr_rules
    aggr_classifier=Classifier(aggr_rules)
    aggr_classifier=aggr_classifier.optimize()
    print "Aggregate Classifier after optimization: ",aggr_classifier
      
     
def main():
    ntot=2
    nin=1  # number of participants with inbound policies
    sdx_participants=generate_sdxglobal(ntot,nin)
    (sdx,participants) = sdx_parse_config('sdx_global.cfg')
    update_paramters(sdx,ntot,nin)
    generate_policies(sdx,participants,ntot,nin)
    aggr_policies=sdx_platform(sdx)
    start_comp=time.time()
    agg_compile=aggr_policies.compile()
    #compiled_parallel=compileParallel(sdx)
    print  'Completed Aggregate Compilation ',time.time() - start_comp, "seconds"
        
    #print "DATA: policy_parl",policy_parl
    #print "DATA: policy_seq ",policy_seq
    #print "Add called ",count_classifierAdd
    print "DATA: add_cache ", add_cache
   

if __name__ == '__main__':
    cProfile.run('main()', 'restats')

    #p = pstats.Stats('restats')
    #p.strip_dirs().sort_stats(-1).print_stats()