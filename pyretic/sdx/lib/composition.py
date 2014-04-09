#############################################
# Policy Composition                        #
# author: Arpit Gupta (glex.qsd@gmail.com)  #
#############################################



from pyretic.sdx.lib.corelib import *


def sdx_from(vport):
    '''
        Helper function that given a vport
        return a match function for all the physical macs behind that vport
        this is useful to avoid communication between two participants
    '''
    match_all_physical_port = no_packets
    for phys_port in vport.participant.phys_ports:
        match_all_physical_port = match_all_physical_port | match(srcmac=phys_port.mac)
    return match_all_physical_port

def sdx_restrict_state(sdx_config, participant):
    '''
        Check if the state is not an end state (i.e., output port). 
        If so return a passthrough policy otherwise 
        prefix a match on the participant's state variable
        before any of the participant's policy to ensure that
        it cannot match on other participant's flowspace
    '''
    match_all_output_var = no_packets
    for output_var in sdx_config.out_var_to_port:
        match_all_output_var = match_all_output_var | match(state=output_var)
    return if_(match_all_output_var, 
               passthrough, 
               match(state=sdx_config.participant_id_to_in_var[participant.id_]) >> 
                    #parallel([sdx_from(participant.peers[peer_name]) for peer_name in participant.peers]) & '''Might not happen, as we are providing limited view to the participants''' 
                        participant.policies
              )

def sdx_preprocessing(sdx_config):
    '''
        Map incoming packets on participant's ports to the corresponding
        incoming state
    '''
    preprocessing_policies = []
    for participant in sdx_config.participants:
        for port in sdx_config.participants[participant].phys_ports:
            preprocessing_policies.append((match(inport=port.id_) >> 
                modify(state=sdx_config.participant_id_to_in_var[sdx_config.participants[participant].id_])))
    return parallel(preprocessing_policies)

def sdx_postprocessing(sdx_config):
    '''
        Forward outgoing packets to the appropriate participant's ports
        based on the outgoing state
    '''
    postprocessing_policies = []
    for output_var in sdx_config.out_var_to_port:
        postprocessing_policies.append((match(state=output_var) >> modify(state=None) >> 
            fwd(sdx_config.out_var_to_port[output_var].id_)))
    return parallel(postprocessing_policies)

def sdx_participant_policies(sdx_config):
    '''
        Sequentially compose the || composition of the participants policy k-times where
        k is the number of participants
    '''
    sdx_policy = passthrough
    for k in [0,1]:
    #for k in sdx_config.participants:
        sdx_policy = sequential([
                sdx_policy,
                parallel(
                    [sdx_restrict_state(sdx_config, sdx_config.participants[participant]) for participant in sdx_config.participants]
                )])
    return sdx_policy

def sdx_platform(sdx_config):
    '''
        Defines the SDX platform workflow. 
        Returns the aggregate composed policy.
    '''
    return (
        sdx_preprocessing(sdx_config) >>
        sdx_participant_policies(sdx_config) >>
        sdx_postprocessing(sdx_config)
    )

if __name__ == '__main__':
    sdx=SDX()
    sdx_platform(sdx)