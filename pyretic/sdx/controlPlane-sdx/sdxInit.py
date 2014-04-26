#############################################
# author: Arpit Gupta (glex.qsd@gmail.com)  #
#############################################


from policyGenerator import *
from policyComposer import *
from common import *
from defaultForwarding import *

import os
import json
import sys
import subprocess
from multiprocessing import Process, Queue


def sdx_init(ntot, nprefixes, nfields, fmult, q=None):
    print "Starting the SDX init with parameters: ", ntot, nprefixes, nfields, fmult
    print '...'
    startexp = time.time()
    print "Update the parameters for this SDX instance"
    # number of ports for the participants with multiple ports
    nports = 2
    nmult = int(ntot * fmult)

    # fraction of prefix groups wrt total prefixes
    fractionGroupc = 0.1

    # Advertised prefix distribution, eg. 10 % participants announce 100% of prefixes,
    # 5 % advertise 20 % of prefixes & 85 % advertise 1% of prefixes announced
    advertisers = [(0.1, 1), (0.05, 0.20), (0.85, 0.01)]

    # Distribution of participant's category, i.e. Tier 1 ISP, Eyeball and
    # Content Provider ISP.
    partTypes = [0.15, 0.05, 0.05, 0.75]

    # Other parameters for policy generation, we'll talk about these
    # parameters later.
    frand = 0.025
    nval = 50

    """
        This function is located in common.py
        It generates the topology configuration file in json format.
    """
    generate_sdxglobal(ntot, nmult, nports)

    """
        This function parses the config file to initialize and configure the SDX's
        platform and participant's data structures.
        loc: ../lib/core.py, common.py
    """
    (sdx, participants) = sdx_parse_config('sdx_global.cfg')
    update_paramters(sdx, ntot, nports)

    """
        Sets the "default forwarding state" for the SDX participant
        This function defines the prefixes advertised by each participant
        and selects the next hop for each of these prefixes (considering both
        uniform/ non-uniform RIB).
    """
    update_bgp(sdx, advertisers, nprefixes, ntot)
    sdx.pfxgrp = sdx.prefixes

    """
        Generates policies for all the participants
    """
    generatePolicies(sdx, participants, ntot, nmult, partTypes, frand, nfields,
                     nval, headerFields, fieldValues)

    """
        Starting the Augmentation of input policies (BGP/VNHs)
    """
    start = time.time()
    vnh_assignment(sdx, participants)
    print "Policy Augmentation: ", time.time() - start

    """
        Compile participant's policies without any composition. Its an inexpensive step
        which updates the cache expediting the compilation of the composed policies.
    """
    print "Composing the augmented policy"
    compile_Policies(participants)

    """
        Calling the composition function
        It returns the number of flow rules generates, compilation time and time to
        augment the policy for this composition scheme.
    """
    start = time.time()
    nRules, compileTime, augmentTime = disjoint_inport_vnhCompose(sdx)
    print nRules, compileTime

    # Get Compiler's cache size
    s1 = total_size(policy_parl, verbose=False)
    s2 = total_size(policy_seq, verbose=False)
    s3 = total_size(disjoint_cache, verbose=False)
    cacheSize = s1 + s2 + s3
    print "Cache sizes: ", cacheSize

    print "Iteration completed in: ", time.time() - startexp
    print "nRules: ",nRules," augmentTime: ", augmentTime," compileTime: ", compileTime, " cacheSize: ",cacheSize
    
    if q is None:
        return (nRules, augmentTime, compileTime, cacheSize)
    else:
        q.put((nRules, augmentTime, compileTime, cacheSize))


if __name__ == '__main__':

    # Total # of participants
    ntot = 20
    # Total # of IP prefixes
    nprefixes = 10
    # Total # of different header fields used in the generated policies
    nfields = 3
    # Fraction of participants with multiple (2 in this case) ports
    fmult = 0.05

    sdx_init(ntot, nprefixes, nfields, fmult)
