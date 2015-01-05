#############################################
# Experiment to evaluate the compilation    #
# times for N participants                #
# author: Arpit Gupta (glex.qsd@gmail.com)  #
#############################################

from common import *
import sys,json
compile_parallel=False

def disjointCompose(sdx):
    disjointPolicies=[]
    print "disjointCompose called"
    for participant in sdx.participants:

        print "Participant",participant.id_,participant.policies
        
        # get list of all participants to which it forwards
        fwdport=extract_all_forward_actions_from_policy(participant.policies)
                
        # print list of forwardports
        #print participant.id_,": ",fwdport
        
        # Remove participant's own ports from the fwdport list        
        fwdport=filter(lambda port: port not in sdx.participant_2_port[participant.id_][participant.id_],fwdport)
        for port in fwdport:
            peer_id=sdx.port_2_participant[int(port)] # Name of fwding participant
            peer=sdx.participants_dict[peer_id] # Instance of fwding participant
                        
            print "Seq compiling policies of part: ",participant.id_," with peer: ",peer_id
            match_ports=no_packets
            for port in sdx.participant_2_port[participant.id_][participant.id_]:
                 match_ports|=match(inport=port)
            
            tmp_policy=match_ports>>participant.policies>>peer.policies
            disjointPolicies.append(tmp_policy)
            
    dPolicy=disjoint(disjointPolicies)
    print "Compile the disjoint policies"
    dclassifier=dPolicy.compile()
    print dclassifier
    return dclassifier
    

def compileParallel(sdx):
    rules_dict={}
    aggr_rules=[]
    
    for participant in sdx.participants:

        print "Participant",participant.id_,participant.policies
        
        # get list of all participants to which it forwards
        fwdport=extract_all_forward_actions_from_policy(participant.policies)
        
        
        # print list of forwardports
        #print participant.id_,": ",fwdport
        
        
        # Remove participant's own ports from the fwdport list        
        fwdport=filter(lambda port: port not in sdx.participant_2_port[participant.id_][participant.id_],fwdport)
        for port in fwdport:
            peer_id=sdx.port_2_participant[int(port)] # Name of fwding participant
            peer=sdx.participants_dict[peer_id] # Instance of fwding participant
                        
            print "Seq compiling policies of part: ",participant.id_," with peer: ",peer_id
            match_ports=no_packets
            for port in sdx.participant_2_port[participant.id_][participant.id_]:
                 match_ports|=match(inport=port)
            
            tmp_policy=match_ports>>participant.policies>>peer.policies
            print "Composed Policies",tmp_policy
            tmp_classifier=tmp_policy.compile()
            
            
            # store the resulting classifier's rules in a dictionary
            rules_dict[(participant.id_,peer_id)]=tmp_classifier.rules
            
    print "Rules Dict: ",rules_dict
    
    
    # Append all the rules in rules dictionary
    for rules in rules_dict.values():
        aggr_rules+=rules[0:len(rules)-1]
    print "aggregate rules: ",aggr_rules
    
    
    # Optimize the classifier from aggregate rules
    aggr_classifier=Classifier(aggr_rules)
    aggr_classifier=aggr_classifier.optimize()
    
    print "Aggregate Classifier after optimization: ",aggr_classifier

def main(argv):
    compile_mode=int(argv[1])

    
    ntot=3
    nin=1  # number of participants with inbound policies
    sdx_participants=generate_sdxglobal(ntot,nin)
    (sdx,participants) = sdx_parse_config('sdx_global.cfg')
    update_paramters(sdx,ntot,nin)
    generate_policies(sdx,participants,ntot,nin)
    start_comp=time.time()
    if compile_mode==0:
        #compiled_parallel=compileParallel(sdx)
        compiled_disjoint=disjointCompose(sdx)
    
    else:
        aggr_policies=sdx_platform(sdx,compile_mode)
        print "Aggregate policy after State Machine Composition",aggr_policies
        agg_compile=aggr_policies.compile()
        print agg_compile
        
        
    print  'Completed Aggregate Compilation ',time.time() - start_comp, "seconds"


if __name__ == '__main__':
    #cProfile.run('main()', 'restats')
    main(sys.argv)