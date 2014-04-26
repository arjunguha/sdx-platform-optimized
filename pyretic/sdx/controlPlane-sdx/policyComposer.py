#############################################
# author: Arpit Gupta (glex.qsd@gmail.com)  #
#############################################

from common import *
from size import *
from policyUtils import * 
import sys
import json

from multiprocessing import Process, Queue
import multiprocessing as mp
import copy

verify = False
debug = True
uniformRIB = True


def get_forwardports(policy, sdx, id):
    """ Extract all the forwarding ports from input policy excluding participant's own"""
    fwdports = extract_all_forward_actions_from_policy(
                policy)
    
    """ Remove participant's own ports from the fwdport list """
    fwdports = filter(
        lambda port: port not in sdx.participant_2_port[id][id], fwdports)
    
    return fwdports
    

def get_inboundPorts(sdx, part_id):
    match_outports = no_packets
    for tmp in sdx.participant_2_port[part_id][part_id]:
        match_outports |= match(outport=tmp)
    match_outports.policies = filter(
        lambda x: x != drop,
        match_outports.policies)
    selfPorts = sdx.participant_2_port[part_id][part_id]
    
    return match_outports, selfPorts


def get_matchPorts(sdx, part_id, peer_id):
    match_inports = no_packets
    for tmp in sdx.participant_2_port[part_id][part_id]:
        match_inports |= match(inport=tmp)
    match_inports.policies = filter(
        lambda x: x != drop,
        match_inports.policies)

    match_outports = no_packets
    for tmp in sdx.participant_2_port[peer_id][peer_id]:
        match_outports |= match(outport=tmp)
    match_outports.policies = filter(
        lambda x: x != drop,
        match_outports.policies)
    
    return match_inports, match_outports
    

def decompose_for_vnhs(sdx):
    """ 
        Decompose policies of all the participants for affected VNHs. 
    """
    if debug:
        print "decompose_for_vnhs called"    
    decomposedPolicies = []
    VNHs = sdx.VNH_2_mac.keys()
    start = time.time()
    decomp = {}
    for vnh in VNHs:
        if vnh != 'VNH':
            # print "Augmenting for mac: ",vnh
            affectedVNH = {}
            affectedVNH[vnh] = sdx.VNH_2_mac[vnh]
            """ Decompose the policy for all participant wrt this affected VNH"""
            decomp[vnh] = processVNH(sdx, affectedVNH, vnh)

    augmentTime2 = time.time() - start
    
    return augmentTime2
    

def disjoint_inport_vnhsReCompose(sdx, affectedVNHs, newVNHs):
    """ Compose for change in VNHs compared to the previous policies """
    disjointPolicies = []
    lowerPolicies = []
    fullDisjoint = True
    cache = False

    for participant in sdx.participants:
        if debug:
            print "Recompose Participant", participant.id_, participant.policiesRecompose

        for ind in range(len(participant.policiesRecompose)):
            # print "Composing policies for update#: ",ind," for participant:
            # ",participant.id_
            fwdports = get_forwardports(participant.policiesRecompose[ind], 
                                       sdx, partcipant.id_)            
            tmp_policy = drop
            for port in fwdports:
                peer_id = sdx.port_2_participant[
                    int(port)]  # Name of fwding participant
                # Instance of fwding participant
                peer = sdx.participants_dict[peer_id]

                if debug:
                    print "2 Seq compiling policies of part: ", participant.id_, " with peer: ", peer_id
                
                match_inports, match_outports = get_matchPorts(sdx, participant.id_, peer_id)

                """ Main logic for policy composition"""
                tmp_policy_peer = (match(dstmac=newVNHs[ind].values()[0]) >> match_inports >> participant.policiesRecompose[
                        ind] >> match_outports >> peer.policiesRecompose[ind] >> match_outports)
                
                if fullDisjoint:
                    tmp_policy_peer = drop + tmp_policy_peer
                    if tmp_policy_peer != drop:
                        # print tmp_policy_peer
                        disjointPolicies.append(tmp_policy_peer)
                else:
                    tmp_policy += tmp_policy_peer
                    # print tmp_policy_participant

            if not fullDisjoint:
                if tmp_policy != drop:
                    disjointPolicies.append(tmp_policy)

    dPolicy = disjoint(disjointPolicies, lowerPolicies, cache)
    if debug:
        print "Compile the disjoint policies"
    start_comp = time.time()
    dclassifier = dPolicy.compile()
    if debug:
        print dclassifier
    nRules = len(dclassifier)
    if debug:
        print nRules
    compileTime = time.time() - start_comp
    if debug:
        print 'Completed Disjoint Compilation ', compileTime, "seconds"
    return nRules, compileTime

    
def disjoint_inport_vnhCompose(sdx):
    """ 
        In this composition scheme, we leverage the fact that flows matching on different VNHs 
        are non-overlapping. We combine this from our previous understanding that flows matching on
        different inports are also non-overlapping. 
        To implement such policy composition, we first decompose the participant's policy wrt all the
        possible VNHs. Each participant will have its own set of policies for each of the defined VNH
        For each VNH, we compose participant's policy matching on inports. Then we finally combine all 
        these policies using Disjoint Policy class. 
    """
    
    """ Decompose the policies for all the VNHs """
    decomposeTime = decompose_for_vnhs(sdx)
    
    """ Now compose all these policies with match on inports """
    disjointPolicies = []
    lowerPolicies = []
    fullDisjoint = True
    if debug:
        print "disjoint_inport_vnhCompose called"

    for participant in sdx.participants:
        if (isDefault(sdx, participant) == False):
            match_outports, selfPorts = get_inboundPorts(sdx, participant.id_)
            
            """ As default forwarding policies are always outbound, its better to get rid of them"""
            inboundPolicy = removeDefault(participant.policies)
            # print "After removing default: ",participant.id_,inboundPolicy
            
            """ 
                Simplify the expressions for inbound policies by removing the outbound policies 
                for each of these participant
            """
            inboundPolicy = simplifyInbound(selfPorts, inboundPolicy)
            
            """ Compose the inbound policies matching on virtual/physical switch (not fully implemented) """
            tmp_policy_participant = match_outports >> inboundPolicy >> match_outports
            """
            if debug: 
                print "Inbound policy for participant: ",participant.id_
                print tmp_policy_participant.compile()
            """
            lowerPolicies.append(tmp_policy_participant)

    # for now ignore the inbound policies
    # lowerPolicies=[]
    for participant in sdx.participants:

        if debug: print " Composing for Participant", participant.id_

        for vnh in participant.decomposedPolicies:

            fwdports = get_forwardports(participant.decomposedPolicies[vnh], sdx, participant.id_)     
            tmp_policy_vnh = drop
            for port in fwdports:
                peer_id = sdx.port_2_participant[
                    int(port)]  # Name of fwding participant
                # Instance of fwding participant
                peer = sdx.participants_dict[peer_id]

                if debug:
                    print "Seq compiling policies of part: ", participant.id_, " with peer: ", peer_id

                match_inports, match_outports = get_matchPorts(sdx, participant.id_, peer_id)
                
                """ Main logic for policy composition"""
                tmp_policy_peer = (match(dstmac=sdx.VNH_2_mac[vnh]) >> match_inports >> participant.decomposedPolicies[
                        vnh] >> match_outports >> peer.decomposedPolicies[vnh] >> match_outports)
                
                
                if fullDisjoint:
                    """ takes care of all the undesired drop cases"""
                    tmp_policy_peer = drop + tmp_policy_peer
                    if tmp_policy_peer != drop:
                        disjointPolicies.append(tmp_policy_peer)
                        if debug:
                            #print tmp_policy_peer
                            print tmp_policy_peer.compile()
                else:
                    tmp_policy_vnh += tmp_policy_peer

            if not fullDisjoint:
                if tmp_policy_vnh != drop:
                    disjointPolicies.append(tmp_policy_vnh)

    dPolicy = disjoint(disjointPolicies, lowerPolicies)
    if debug:
        print "Compile the disjoint policies"
    start_comp = time.time()
    dclassifier = dPolicy.compile()
    if debug:
        print dclassifier
    nRules = len(dclassifier)

    if debug:
        print nRules
    compileTime = time.time() - start_comp
    if debug:
        print 'Completed Disjoint Compilation ', compileTime, "seconds"
    
    return nRules, compileTime, decomposeTime


def disjoint_inportCompose(sdx):
    """
        Disjoint Policies: Two policies are called disjoint if 
        they are applied over non-overlapping flows. We observed 
        that flows entering from different inports exist in disparate
        flow-space. We leverage this observation to simplify policy
        composition/compilation for SDX. Consider this example:
        Participant: 1,2,3 with policies p1,p2,p3. p1 & p3 have forwarding action
        for 3. With LSM policy composition will be: (p1>>p3)+(p2>>p3). Now observe that
        flows entering from 1's port will have inport = 1 and similarly one entering from
        2 will have inport = 2. The two flows are non-overlapping thus "+" operation between
        p1>>p3 and p2>>p3 is an overkill. A flow will either match for inport=1 or 2. Thus the
        policies match(inport=1)>>p1>>p3 is disjoint with policy match(inport=2)>>p2>>p3.
        We defined a Disjoint Class of policies which evaluates the classifier o/p for all
        these disjoint policies.   
        
    """
    
    fullDisjoint = True
    disjointPolicies = []
    lowerPolicies = []
    if debug:
        print "disjoint_inportCompose called"

    """ Lower priority disjoint inbound policies"""
    for participant in sdx.participants:
        if (isDefault(sdx, participant) == False):            
            match_outports, selfPorts = get_inboundPorts(sdx, participant.id_)            
            
            """ Compose the inbound policies matching on virtual/physical switch """
            tmp_policy_participant = match_outports >> participant.policies >> match_outports
            lowerPolicies.append(tmp_policy_participant)


    for participant in sdx.participants:

        if debug:
            print "Participant", participant.id_, participant.policies

        # get list of all participants to which it forwards
        fwdports = get_forwardports(participant.policies, 
                                       sdx, partcipant.id_)     
        
        tmp_policy_participant = drop
        pdict = {}
        if debug:
            print participant.policies.compile()
        for port in fwdports:
            # Name of fwding participant
            peer_id = sdx.port_2_participant[
                int(port)] 
            # Instance of fwding participant
            peer = sdx.participants_dict[peer_id]

            if debug:
                print "Seq compiling policies of part: ", participant.id_, " with peer: ", peer_id

            match_inports, match_outports = get_matchPorts(sdx, participant.id_, peer_id)
            
            """ Main logic for policy composition"""
            tmp_policy_peer = (match_inports >> participant.policies >>
                    match_outports >> peer.policies >> match_outports)
            
            if fullDisjoint:
                tmp_policy_peer = drop + tmp_policy_peer
                if tmp_policy_peer != drop:
                    disjointPolicies.append(tmp_policy_peer)
            else:
                tmp_policy_participant += tmp_policy_peer

        if not fullDisjoint:
            if tmp_policy_participant != drop:
                disjointPolicies.append(tmp_policy_participant)

    dPolicy = disjoint(disjointPolicies, lowerPolicies)
    if debug:
        print "Compile the disjoint policies"
    start_comp = time.time()
    dclassifier = dPolicy.compile()
    if debug:
        print dclassifier
    nRules = len(dclassifier)
    if debug:
        print nRules
    compileTime = time.time() - start_comp
    if debug:
        print 'Completed Disjoint Compilation ', compileTime, "seconds"
    return nRules, compileTime



def lsmCompose(sdx):
    """ 
        This is the Lean State Machine Policy Composition approach.
        naive composition is: P = (p1+p2+p3+...pn) >> (p1+p2+p3+...)
        We observed that such policy composition is very expensive in terms of compilation time. 
        Specially the parallel operation for all the participant's policies. 
        Simplifying the above expression using netkat semantics:
        P = (p1>>p2+p1>>p3+...+p1>>pn)+(p2>>p1+p2>>p3+...+p2>>pn)+...
        Note that if participant 1 has forwarding poliy for 2 only then we are wasting precious
        compilation time composing/compiling p1>>p3, p1>>p4 etc. In this approach we streamline 
        the state machine by the forwarding peer and limiting the number of policy compositions.
    """
    lsmPolicies = []
    if debug:
        print "lsmCompose called"
    lowerPolicies = []
    # take into consideration the participants with inbound policies
    # They need to be composed in parallel with other policies
    for participant in sdx.participants:
        if (isDefault(sdx, participant) == False):
            match_outports = no_packets
            for tmp in sdx.participant_2_port[participant.id_][participant.id_]:
                match_outports |= match(outport=tmp)
            match_outports.policies = filter(
                lambda x: x != drop,
                match_outports.policies)
            tmp_policy_participant = match_outports >> participant.policies >> match_outports
            lowerPolicies.append(tmp_policy_participant)

    for participant in sdx.participants:

        if debug:
            print "Participant", participant.id_, participant.policies
        # get list of all participants to which it forwards
        fwdports = get_forwardports(participant.policies, 
                                       sdx, partcipant.id_)         
        tmp_policy_participant = drop
        pdict = {}
        if debug:
            print participant.policies.compile()
        for port in fwdports:
            peer_id = sdx.port_2_participant[
                int(port)]  # Name of fwding participant
            # Instance of fwding participant
            peer = sdx.participants_dict[peer_id]

            if debug:
                print "Seq compiling policies of part: ", participant.id_, " with peer: ", peer_id
            match_inports, match_outports = get_matchPorts(sdx, participant.id_, peer_id)
            
            """ 
                Compiling: A(outbound) >> B (inbound):
                Match for inport of to filter flows entering from other inports.
                Apply A's policies and filter out flows going out to B matching on B's outports. 
                Then apply B's policies and filter for flows entering B's physical ports. s
            """
            tmp_policy_participant += (match_inports >> participant.policies >>
                           match_outports >> peer.policies >> match_outports)

        # print tmp_policy_participant
        if debug:
            print tmp_policy_participant.compile()
        lsmPolicies.append(tmp_policy_participant)
    
    lsmPolicies += lowerPolicies
    lPolicy = parallel(lsmPolicies)
    
    if debug:
        print "Compile the lsm policies"
    start_comp = time.time()
    lclassifier = lPolicy.compile()
    if debug:
        print lclassifier
    nRules = len(lclassifier)
    if debug:
        print nRules
    compileTime = time.time() - start_comp
    if debug:
        print 'Completed lsm Compilation ', compileTime, "seconds"
    return nRules, compileTime


def naiveCompose(sdx):
    """ This is the k-step composition we presented in the Tech Report """

    if debug:
        print "naiveCompose called"
    compile_mode = 1
    nPolicy = sdx_platform(sdx, compile_mode)
    if debug:
        print "Compile the naive policies"
    start_comp = time.time()
    nclassifier = nPolicy.compile()
    if debug:
        print nclassifier
    nRules = len(nclassifier)
    if debug:
        print nRules
    compileTime = time.time() - start_comp
    if debug:
        print 'Completed naive Compilation ', compileTime, "seconds"
    return nRules, compileTime

