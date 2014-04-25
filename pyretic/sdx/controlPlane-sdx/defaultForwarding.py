#############################################
# author: Arpit Gupta (glex.qsd@gmail.com)  #
#############################################

from common import *
from size import *
import sys
import json

from multiprocessing import Process, Queue
import multiprocessing as mp

verify = False
debug = False
uniformRIB = True


def divideAdvertisers(advertisers, ntot):
    n1, x = advertisers[0]
    n2, x = advertisers[1]
    n1 *= (ntot)
    n2 *= ntot

    n1 = int(n1)
    n2 = int(n2)

    if n1 == 0:
        n1 = 1
    if n2 == 0:
        n2 = 1
    n2 += n1

    return n1, n2


def getPrefixes(sdx, n):
    """ Creates representative IP prefixes"""
    pfxes = {}
    for i in range(n):
        # modify later to get real IP prefixes here
        tmp = 'pg' + str(i + 1)
        pfxes[tmp] = [tmp]
    sdx.prefixes = pfxes


def getPrefixAnnounced(k, sdx):
    return random.sample(sdx.prefixes, k)


def update_prefix2part(prefix2part, sdx, id):
    """ """
    for pfx in sdx.prefixes_announced['pg1'][id]:
        if pfx not in prefix2part:
            prefix2part[pfx] = []
        prefix2part[pfx].append(id)


def getAdvertisedPrefixes(sdx, n1, n2, advertisers):
    N = len(sdx.prefixes.keys())
    frac = 0.0
    prefix2part = {}
    for participant in sdx.participants:
        if int(participant.id_) <= n1:
            # top advertisement prefixes
            if debug:
                print "top advertiser", participant.id_
            x, frac = advertisers[0]
        elif int(participant.id_) > n1 and int(participant.id_) <= n2:
            # middle level advertisers
            x, frac = advertisers[1]
        else:
            # low level advertisers
            x, frac = advertisers[2]
        nfrac = int(frac * N)
        if nfrac == 0:
            nfrac = 1
        # print nfrac
        sdx.prefixes_announced['pg1'][
            participant.id_] = getPrefixAnnounced(
            nfrac,
            sdx)
        update_prefix2part(prefix2part, sdx, participant.id_)
    if debug:
        print sdx.prefixes_announced
    sdx.prefix2part = prefix2part

    return prefix2part


def update_bgp(sdx, advertisers, nprefixes, ntot):
    if debug:
        print "Update BGP called"

    """ Generate IP prefixes (currently representative ones like p1,p2 etc.) """
    getPrefixes(sdx, nprefixes)

    """ Get advertiser distribution """
    n1, n2 = divideAdvertisers(advertisers, ntot)

    """ Get prefixes announced by each participant """
    prefix2part = getAdvertisedPrefixes(sdx, n1, n2, advertisers)

    """
        Get ebgp NH for RS with either unform RIB or non-uniform RIB.
        Uniform RIB: All participants select the same NH for all the prefixes.
        We consider Uniform RIB until otherwise stated.
    """
    if uniformRIB:
        ebgp_nh_received = {}

        # bias favoring selection of top advertiser as bgp NH
        biasFactor = 10

        for prefix in sdx.prefixes:
            tmp = []
            for elem in prefix2part[prefix]:
                if int(elem) <= n1:
                    # biasing the result in favor of only one top advertisers
                    for i in range(biasFactor * len(prefix2part[prefix])):
                        tmp.append(elem)
                else:
                    tmp.append(elem)
            ebgp_nh_received[prefix] = random.choice(tmp)

        participant_to_ebgp_nh_received = {}
        for participant in sdx.participants:
            participant_to_ebgp_nh_received[participant.id_] = ebgp_nh_received

    else:
        # Now assign the ebgp nh
        participant_to_ebgp_nh_received = {}
        for participant in sdx.participants:
            if participant.id_ not in participant_to_ebgp_nh_received:
                participant_to_ebgp_nh_received[participant.id_] = {}

            # bias the nh decision in favor of top advertisers
            biasFactor = 1
            for prefix in sdx.prefixes:
                if prefix not in sdx.prefixes_announced['pg1'][participant.id_]:
                    tmp = []
                    for elem in prefix2part[prefix]:
                        if int(elem) <= n1:
                            for i in range(biasFactor * len(prefix2part[prefix])):
                                tmp.append(elem)

                        else:
                            tmp.append(elem)
                    participant_to_ebgp_nh_received[
                        participant.id_][prefix] = random.choice(tmp)

    if debug:
        print "ebgp updated: ", participant_to_ebgp_nh_received
    best_paths = get_bestPaths(participant_to_ebgp_nh_received)
    sdx.best_paths = best_paths
    if debug:
        print "best paths: ", best_paths
    sdx.participant_to_ebgp_nh_received = participant_to_ebgp_nh_received
