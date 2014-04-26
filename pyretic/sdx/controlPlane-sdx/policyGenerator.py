#############################################
# author: Arpit Gupta (glex.qsd@gmail.com)  #
#############################################

from common import *
from size import *
import sys
import json

from multiprocessing import Process, Queue
import multiprocessing as mp
import copy

verify = False
debug = True
uniformRIB = True

headerFields = ['dstport', 'srcport', 'srcip']
fieldValues = {'dstport': range(1, 101), 'srcport': range(1, 101),
               'srcip': list(IPNetwork('172.0.0.1/26'))}


def divideParticipants(partTypes, ntot):
    nparts = []
    for i in range(len(partTypes) - 1):
        tmp = int(partTypes[i] * ntot)
        if tmp == 0:
            tmp = 1
        nparts.append(tmp)
    nparts.append(ntot - sum(nparts))
    n1 = nparts[0]
    n2 = sum(nparts[0:2])
    n3 = sum(nparts[0:3])

    return n1, n2, n3, nparts


def normalizePrefixSets(sdx, nparts, fracPG):
    tmp = sdx.pfxgrp.keys()
    div = int(float(len(tmp)) / nparts[0])
    if debug:
        print 'DIV:', div
    part2prefixset = {}
    for i in range(nparts[0] - 1):
        k = i * div
        part2prefixset[i + 1] = tmp[k:k + div]
    k = (nparts[0] - 1) * div
    part2prefixset[nparts[0]] = tmp[k:]
    # print "Before Normalization: ",part2prefixset
    N = len(sdx.pfxgrp.keys())
    N1 = int(N * fracPG)
    if N1 == 0:
        N1 = 1
    # N1=5
    p = len(part2prefixset[1])
    # print N1,p
    if debug:
        print 'Before normalization, part2prefixset: ', part2prefixset
    if p < N1:
        # Add more prefixes to maintain that each participant has policies for at least 5%
        # print "Needs Change"
        for k in part2prefixset:
            if k != n1:
                new = random.sample(tmp, N1 - p)
                part2prefixset[k] += new

    return part2prefixset


def divideEyeballFORcontent(n1, n2, n3):
    tmp = range(1, n1 + 1)
    div = int(float(len(tmp)) / (n3 - n2))
    eyeballFORcontent = {}
    kys = range(n2 + 1, n3)
    for i in kys:
        k = (i - (n2 + 1)) * div
        eyeballFORcontent[i] = tmp[k:k + div]
    k = (n3 - n2 - 1) * div
    eyeballFORcontent[n3] = tmp[k:]

    return eyeballFORcontent


def setPred(field, val):
    if field == 'dstport':
        return match(dstport=val)
    elif field == 'srcport':
        return match(srcport=val)
    elif field == 'srcip':
        return match(srcip=val)
    elif field == 'match_prefixes_set':
        return match_prefixes_set(val)


def getPred(headerFields, fieldValues, nfields):
    nfields = 1
    # print headerFields
    fields = random.sample(headerFields, nfields)
    packet = identity
    for field in fields:
        if field in fieldValues:
            val = random.choice(fieldValues[field])
            packet = packet >> (setPred(field, val))
    packet.policies = filter(lambda x: x != identity, packet.policies)

    return packet


def getDisjointPolicies(pdict):
    # print pdict
    # if len(pdict.keys())>0:
    k = pdict.keys()[0]
    v = pdict[k]
    pdict.pop(k, v)

    if k != identity:
        # print "k:",k.policies
        if isinstance(k, sequential):
            # print "seq"
            pred = identity
            for pol in k.policies:
                # print pol,pred
                pred = intersection([pred, pol])
                # print pred

            #pred.policies=filter(lambda x:x!=identity,pred.policies)
        elif isinstance(k, parallel):
            # print "++"
            pred = drop
            for pol in k.policies:
                pred |= pol
            pred.policies = filter(lambda x: x != drop, pred.policies)
        elif isinstance(k, union):
            # print "union"
            pred = drop
            for pol in k.policies:
                pred |= pol
            pred.policies = filter(lambda x: x != drop, pred.policies)
        elif isinstance(k, intersection):
            # print "intersection"
            pred = identity
            for pol in k.policies:
                pred = pred and pol
            #pred.policies=filter(lambda x:x!=identity,pred.policies)

    else:
        pred = identity
    # print "pred: ",pred
    t = v
    f = None
    # print "rem: ",pdict
    if len(pdict.keys()) >= 1:
        # print len(pdict.keys())
        f = getDisjointPolicies(pdict)
        # print "f: ",f
    else:
        f = drop

    return if_(pred, t, f)


def updateHeaderFields(headerFields, fieldValues, nval, nfields):
    """
        Logic for selecting the header fields and their possible values.
    """
    # Randomly sample which header fields will be used for participant's
    # "Outbound" policies
    headerFields = random.sample(headerFields, nfields)

    # Randomly sample the header field values for each field
    for k in fieldValues:
        fieldValues[k] = random.sample(fieldValues[k], nval)

    # Repeating the same thing for Inbound policies.
    # Currently ignoring inbound policies matching on dstip
    headerFieldInbound = random.sample(headerFields, nfields)
    for k in fieldValues:
        fieldValues[k] = random.sample(fieldValues[k], nval)

    return headerFields, headerFieldInbound, fieldValues


def generatePolicies(sdx, participants, ntot, nmult, partTypes, frand, nfields,
                     nval, headerFields, fieldValues):
    """ Update the header fields to be used for the generated policies"""
    headerFields, headerFieldInbound, fieldValues = updateHeaderFields(
        headerFields, fieldValues, nval, nfields)
    if debug:
        print "Samples header field values: ", fieldValues

    """
        Logic to divide the policies for top eyeballs, top content and others
        1: Tier 1 ISPs (5%) (1->n1)
        2: Tier 2 ISPs (15%) (n+1->n2)
        3: Top Content (5%) (n2+1->n3)
        4: Others (useless fellows) n3+
    """
    n1, n2, n3, nparts = divideParticipants(partTypes, ntot)
    if debug:
        print "Participant Division: ", n1, n2, n3

    """
        Logic to equally divide prefix sets announced by each Tier1 ISPs.
        Why? This steps are required to avoid performance bias where we increase # of participants
        for same # of prefix sets. This division approach ensures that there are atleast
        certain ("fracPG") fraction of prefixes for which each tier 1 participant has policies.
    """

    fracPG = 0.06  # 6%
    # part2prefixset: dictionary which maps participants to dstip prefixes
    # used for its outbound policies
    part2prefixset = normalizePrefixSets(sdx, nparts, fracPG)
    if debug:
        print "Prefix Set: ", part2prefixset

    """
        Logic to equally divide the eyeball ISPs among the content providers for writing
        their outbound policies.
    """
    eyeballFORcontent = divideEyeballFORcontent(n1, n2, n3)
    if debug:
        print "EB:", eyeballFORcontent

    """
        nSample: is used for random sampling, "frand" determines what fraction of total
        participants we'll sample
    """
    nSample = int(frand * ntot)
    if nSample == 0:
        nSample = 1

    # If we want more rules for top eyeballs and content providers
    intensityFactor = 2

    # This is used to keep track of all the prefixes for which we have inbound policies
    # for each participant. Helps in VNH Assignment!
    inbound = {}

    """ Generating policies for each participant """
    for participant in sdx.participants:
        sdx.part2pg[participant.id_] = []

        """
            We store participant's policies as a dictionary. This helps us in making
            sure that all the policies for each participant are non-overlapping.
            That is for each incoming flow there is only one possible output port.
            For eg. If participant A has the policy two policies:
            match(dstport = 80)>> fwd(B), match(srcport = 22) >> fwd(C)
            One way of expressing these two policies is using + composition i.e.
            match(dstport = 80)>> fwd(B) + match(srcport = 22) >> fwd(C)
            But this will imply that for flow with dstport=80 & srcport 22 output
            port will be both B and C. This is neither desired nor supported in SDX.
            In this example we do random ordering of participant's policies and use if_()
            to ensure that there is only one resulting outport.
            
        """
        policyDict = {}

        policy = drop
        if debug:
            print 'participant: ', participant.id_
        sdx.participant_2_port[participant.id_][participant.id_]

        inbound[participant.id_] = []
        if int(participant.id_) <= n1:

            if debug:
                print "Generating policies for Tier1 ISPs"

            # Inbound policies for traffic coming from top content folks
            topContent = random.sample(range(n2 + 1, n3 + 1), nSample)
            for pid in topContent:
                tmp = getPred(headerFieldInbound, fieldValues, nfields)
                if debug:
                    print "tier 1 inbound pred", tmp
                assert(isinstance(tmp, sequential))
                pred = tmp.policies[0]

                # Keep track of prefixes used for inbound policies
                if isinstance(pred, match_prefixes_set):
                    pfx = (list(pred.pfxes))[0]
                    inbound[participant.id_].append(pfx)

                # storing the generated policies as a dict
                policyDict[tmp] = fwd(
                    random.choice(
                        participant.phys_ports).id_)

        elif int(participant.id_) > n1 and int(participant.id_) <= n2:
            if debug:
                print "Generating policies for Tier 2 ISPs"

            # inbound policies for few top content participants
            topContent = random.sample(range(n2 + 1, n3 + 1), nSample)
            for pid in topContent:
                tmp = getPred(headerFieldInbound, fieldValues, nfields)
                if debug:
                    print "tier 2 inbound pred", tmp.policies
                assert(isinstance(tmp, sequential))
                pred = tmp.policies[0]
                if isinstance(pred, match_prefixes_set):
                    pfx = (list(pred.pfxes))[0]
                    inbound[participant.id_].append(pfx)

                policyDict[tmp] = fwd(
                    random.choice(
                        participant.phys_ports).id_)

            # outbound policies for few top eyeballs
            topEyeballs = random.sample(range(1, n1), nSample)
            for pid in topEyeballs:
                announced = sdx.pfxgrp.keys()
                pfxset = random.choice(announced)
                tmp = getPred(headerFields, fieldValues, nfields)

                # Combining the match on prefix set and other header fields
                tmp = (match_prefixes_set(sdx.pfxgrp[pfxset]) >> tmp)
                sdx.part2pg[participant.id_].append(sdx.pfxgrp[pfxset][0])

                # TODO use sdx.fwd() to avoid using physical port of peers
                policyDict[tmp] = fwd(
                    participant.peers[
                        str(pid)].participant.phys_ports[0].id_)

        elif int(participant.id_) > n2 and int(participant.id_) <= n3:
            if debug:
                print "Generating policies for content providers"

            # outbound policies for top eyeballs
            topeyeballs = eyeballFORcontent[int(participant.id_)]

            for pid in topeyeballs:
                if pid != n1:
                    for pfxset in random.sample(part2prefixset[pid], len(part2prefixset[pid])):
                        t1 = (match_prefixes_set(sdx.pfxgrp[pfxset]))
                        sdx.part2pg[
                            participant.id_].append(
                            sdx.pfxgrp[pfxset][0])
                        t2 = (getPred(headerFields, fieldValues, nfields))
                        t = [t1, t2]
                        tmp = t1 >> t2
                        policyDict[tmp] = fwd(
                            participant.peers[
                                str(pid)].participant.phys_ports[0].id_)

            # inbound policies for randomly selected tier2
            tier2 = random.sample(range(n1 + 1, n2 + 1), 1)
            if debug:
                print tier2
            for pid in tier2:
                tmp = getPred(headerFieldInbound, fieldValues, nfields)
                if debug:
                    print " content inbound pred", tmp
                assert(isinstance(tmp, sequential))
                pred = tmp.policies[0]
                if isinstance(pred, match_prefixes_set):
                    pfx = (list(pred.pfxes))[0]
                    inbound[participant.id_].append(pfx)
                policyDict[tmp] = fwd(
                    participant.phys_ports[random.choice(range(len(participant.phys_ports)))].id_)

        else:
            if debug:
                print "Generating policies for others"

            # These non-important members will write default policies
            # Transform virtual port to one of their physical ports
            match_ports1 = no_packets
            for tmp in sdx.participant_2_port[participant.id_][participant.id_]:
                match_ports1 |= match(outport=tmp)
            match_ports1.policies = filter(
                lambda x: x != drop,
                match_ports1.policies)
            policyDict[match_ports1] = fwd(
                participant.phys_ports[random.choice(range(len(participant.phys_ports)))].id_)

        """
            This is to ensure that participants have no ambiguity in its forwarding action
            All rules are iteratively applied with if_ class of rules. Refer the description of
            policyDict above for details.
        """
        policy = getDisjointPolicies(policyDict)

        if debug:
            print "Generated policy: "
            print policy

        participant.policies = policy
        participant.original_policies = participant.policies

    sdx.inbound = inbound
