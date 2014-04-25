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
debug = False
uniformRIB = True


def removeDefault(policy):
    if isinstance(policy, if_):
        return policy.t_branch
    else:
        return policy


def simplifyInbound(selfPorts, policy):
    if isinstance(policy, if_):
        assert(isinstance(policy.t_branch, fwd))
        fwdport = policy.t_branch.outport
        if fwdport in selfPorts:
            return if_(
                policy.pred,
                policy.t_branch,
                simplifyInbound(
                    selfPorts,
                    policy.f_branch))
        else:
            return simplifyInbound(selfPorts, policy.f_branch)
    else:
        return policy


def isDefault(sdx, participant):
    policy = participant.policies
    assert(isinstance(policy, if_))
    assert(isinstance(policy.pred, union))
    tmp = policy.pred.policies[0]
    # assert(isinstance(tmp,match))

    if isinstance(tmp, match):
        if 'outport' in tmp.map:
            # print participant.id_," is default",tmp.map
            return True

        else:
            # print participant.id_," is non-default",tmp.map
            return False
    else:
        # print participant.id_," is not default"
        return False


def copyPolicy(pol):
    newpol = None
    if isinstance(pol, if_):
        newpol = if_(
            copyPolicy(
                pol.pred), copyPolicy(
                pol.t_branch), copyPolicy(
                pol.f_branch))
    else:
        tmp = []
        if hasattr(pol, 'policies'):
            for plc in pol.policies:
                tmp.append(copyPolicy(plc))
            pol.policies = tmp
            newpol = pol
        else:
            if pol == drop:
                newpol = drop
            if pol == identity:
                newpol = identity
            newpol = copy.copy(pol)
    return newpol


def processVNH_MULTI(participants, affectedVNH, vnh, q=None):
    start1 = time.time()
    decomp = {}
    for part in participants:
        
        start2 = time.time()
        tmp = traverse(part.policies, affectedVNH, affectedVNH)
        decomp[part.id_] = copyPolicy(tmp)

    if q is not None:
        q.put(decomp)
        if (debug):
            print "Put operation completed", mp.current_process()
    else:
        return decomp


def processVNH(sdx, affectedVNH, vnh):
    start1 = time.time()
    decomp = {}
    for part in sdx.participants:

        start2 = time.time()
        """ traverses participant's policy tree and returns policy tree specific to affected VNH"""
        # TODO: update why we have repetition of input parameter (affectedVNH)
        tmp = traverse(part.policies, affectedVNH, affectedVNH)
        part.decomposedPolicies[vnh] = tmp
        decomp[part.id_] = tmp

    return decomp


def traverse(policy, affectedVNH, newVNH):
    """ 
        Recursively traverses a policy tree and replaces the affected VNH with new one.
        It returns policy tree specific to affected VNH.
    """
    if isinstance(policy, intersection):
        # print policy
        tmp = intersection(
            map(lambda p: traverse(p, affectedVNH, newVNH), policy.policies))
        flag = False

        # print tmp.policies
        for pol in tmp.policies:
            if isinstance(pol, match):
                # if 'dstmac' in pol.map:
                flag = True
            if isinstance(pol, union) or isinstance(pol, parallel) or isinstance(pol, intersection):
                flag = True
        if flag:
            # print "App match pol: ",tmp
            tmp.policies = filter(lambda p: p != identity, tmp.policies)
            # print "App post filter: ",tmp
            if drop not in tmp.policies:
                return tmp
            else:
                return union([])
        else:
            return union([])

    elif isinstance(policy, union):
        # print "init",policy

        tmp = union(
            map(lambda p: traverse(p, affectedVNH, newVNH), policy.policies))
        flag = False
        # print policy.policies
        for pol in tmp.policies:
            if isinstance(pol, match):
                # if 'dstmac' in pol.map:
                flag = True
            if isinstance(pol, union) or isinstance(pol, parallel) or isinstance(pol, intersection):
                flag = True
        if flag:
            # print "App match pol: ",tmp
            tmp.policies = filter(lambda p: p != drop, tmp.policies)
            # print "App post filter: ",tmp
            return tmp
        else:
            return union([])

    elif isinstance(policy, parallel):
        # print "++ before",policy.policies
        tmp = parallel(
            map(lambda p: traverse(p, affectedVNH, newVNH), policy.policies))
        tmp.policies = filter(lambda p: p != drop, tmp.policies)
        # print "++ ater",tmp.policies
        flag = False
        # print policy.policies
        for pol in tmp.policies:
            if isinstance(pol, match):
                if 'dstmac' in pol.map:
                    flag = True
            elif isinstance(pol, sequential):
                flag = True

        if flag:
            # print "++App match pol: ",tmp
            tmp.policies = filter(lambda p: p != drop, tmp.policies)
            # print "++App post filter: ",tmp
            return tmp
        else:
            return union([])

        return tmp

    elif isinstance(policy, sequential):
        tmp = sequential(
            map(lambda p: traverse(p, affectedVNH, newVNH), policy.policies))
        #tmp.policies=filter(lambda p:p!=drop,tmp.policies)
        if drop in tmp.policies:
            return drop
        else:
            return tmp
    elif isinstance(policy, if_):
        # if debug==True: print policy
        pred = traverse(policy.pred, affectedVNH, newVNH)
        t = traverse(policy.t_branch, affectedVNH, newVNH)
        f = traverse(policy.f_branch, affectedVNH, newVNH)
        if pred == drop:
            return f
        else:
            return if_(traverse(policy.pred, affectedVNH, newVNH),
                       traverse(policy.t_branch, affectedVNH, newVNH),
                       traverse(policy.f_branch, affectedVNH, newVNH))
    else:
        if isinstance(policy, match):
            if 'dstmac' in policy.map:
                # print policy.map['dstmac']
                if policy.map['dstmac'] == affectedVNH.values()[0]:
                    # print "Affected mac found"
                    return match(dstmac=newVNH.values()[0])
                else:
                    return drop
            else:
                return policy
        else:
            return policy