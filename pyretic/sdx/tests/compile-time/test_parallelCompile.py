#############################################
# Experiment to evaluate the compilation    #
# times for N participants                #
# author: Arpit Gupta (glex.qsd@gmail.com)  #
#############################################

from common import *


def compileParallel(sdx):
    rules_dict={}
    aggr_rules=[]
    
    for participant in sdx.participants:

        print "Participant",participant.id_,participant.policies
        
        # get list of all participants to which it forwards
        fwdport=extract_all_forward_actions_from_policy(participant.policies)
        
        
        # print list of forwardports
        print participant.id_,": ",fwdport
        
        
        # Remove participant's own ports from the fwdport list        
        fwdport=filter(lambda port: port not in sdx.participant_2_port[participant.id_][participant.id_],fwdport)
        for port in fwdport:
            peer_id=sdx.port_2_participant[int(port)] # Name of fwding participant
            peer=sdx.participants_dict[peer_id] # Instance of fwding participant
                        
            print "Seq compiling policies of part: ",participant.id_," with peer: ",peer_id          
            tmp_policy=participant.policies>>peer.policies
            tmp_classifier=tmp_policy.compile()
            
            # store the resulting classifier's rules in a dictionary
            rules_dict[(participant.id_,peer_id)]=tmp_classifier.rules
            
    print "Classifier Dict: ",rules_dict
    
    
    # Append all the rules in rules dictionary
    for k,v in rules_dict.iteritems():
        aggr_rules+=v
    print "aggregate rules: ",aggr_rules
    
    
    # Optimize the classifier from aggregate rules
    aggr_classifier=Classifier(aggr_rules)
    aggr_classifier=aggr_classifier.optimize()
    
    print "Aggregate Classifier after optimization: ",aggr_classifier

def main():

    ntot=10
    nin=1  # number of participants with inbound policies
    sdx_participants=generate_sdxglobal(ntot,nin)
    (sdx,participants) = sdx_parse_config('sdx_global.cfg')
    update_paramters(sdx,ntot,nin)
    generate_policies(sdx,participants,ntot,nin)
    start_comp=time.time()
    compiled_parallel=compileParallel(sdx)
    print  'Completed Aggregate Compilation ',time.time() - start_comp, "seconds"


if __name__ == '__main__':
    cProfile.run('main()', 'restats')
