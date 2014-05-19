## Pyretic-specific imports
from pyretic.lib.corelib import *
from pyretic.lib.std import *

from pyretic.modules.arp import *
from pyretic.modules.mac_learner import *
from netaddr import *

# IXP's subnet
ixp_prefixes = list(IPNetwork('66.66.0.0/28'))

# Advertised IP prefixes
prefixes = {'p1':IPNetwork('100.0.1.0/24'), 'p2':IPNetwork('100.0.2.0/24'),
            'p3':IPNetwork('100.0.3.0/24'), 'p4':IPNetwork('100.0.4.0/24'),
            'p5':IPNetwork('100.0.5.0/24'), 'p6':IPNetwork('130.0.0.0/24')}

# Mac addresses
mac_a1 = '00:00:00:00:00:01'
mac_b1 = '00:00:00:00:00:02'
mac_b2 = '00:00:00:00:00:03'
mac_c1 = '00:00:00:00:00:04'

""" 
Ports
A1 = 1, A = 5
B1 = 2, B1 = 6
B2 = 3, B2 = 7
C1 = 4, C = 8
"""

def sigcomm_example():
    P_A = (((match(dstip = prefixes['p1'])|match(dstip = prefixes['p2'])|
            match(dstip = prefixes['p4'])) >> fwd(8)) + 
            (match(dstip = prefixes['p3']) >> fwd(6)))
    
    """
    BGP_A = (((match(dstip = prefixes['p1'])|match(dstip = prefixes['p2'])|
            match(dstip = prefixes['p4'])) >> fwd(3)) + 
            (match(dstip = prefixes['p3']) >> fwd(2)))
    
    big_match_prefix = ((match(dstip = prefixes['p1'])|match(dstip = prefixes['p2'])|
            match(dstip = prefixes['p3'])|match(dstip = prefixes['p4'])))
                        
    """
    
    big_match_sdx_A = ((match(dstport = 80)|match(dstport = 443)))
    
    default_A = ((match(dstmac = mac_b1) >> fwd(6)) + (match(dstmac = mac_b2) >> fwd(7))+
            (match(dstmac = mac_c1) >> fwd(8))+(match(dstmac = mac_a1) >> fwd(5))+
            (match(outport=5) >> modify(dstmac = mac_a1) >> fwd(1)))
    
    #non_default_A = if_(big_match_sdx_A, P_A, BGP_A)
    
    #augmented_A = if_(big_match_prefix, non_default_A, default_A)
    augmented_A = (if_(big_match_sdx_A, P_A, default_A))
    
    default_B = ((match(dstmac = mac_b1) >> fwd(6)) + (match(dstmac = mac_b2) >> fwd(7))+
            (match(dstmac = mac_c1) >> fwd(8))+(match(dstmac = mac_a1) >> fwd(5))+
            (match(outport=6)>> modify(dstmac = mac_b1) >> fwd(2))+
            (match(outport=7)>> modify(dstmac = mac_b2) >> fwd(3)))
    
    default_C = ((match(dstmac = mac_b1) >> fwd(6)) + (match(dstmac = mac_b2) >> fwd(7))+
            (match(dstmac = mac_c1) >> fwd(8))+(match(dstmac = mac_a1) >> fwd(5))+
            (match(outport=8)>> modify(dstmac = mac_c1) >>fwd(4)))
    
    augmented_B = (default_B)
    augmented_C = (default_C)
    
    #compose the policies in efficient manner
    disjoint_policies = []
    disjoint_policies.append((match(inport = 1)) >> augmented_A >> 
                             match(outport = 5) >> augmented_A >> (match(outport = 1))) 
    disjoint_policies.append((match(inport = 1)) >> augmented_A >> 
                             (match(outport = 6) | match(outport = 7)) >> augmented_B >> 
                             (match(outport = 2) | match(outport = 3)))
    disjoint_policies.append((match(inport = 1)) >> augmented_A >> 
                             match(outport = 8) >> augmented_C >> (match(outport = 4))) 
    
    disjoint_policies.append((match(inport = 2)| match(inport = 3)) >> augmented_B >> 
                             match(outport = 5) >> augmented_A >> (match(outport = 1))) 
    disjoint_policies.append((match(inport = 2)| match(inport = 3)) >> augmented_B >> 
                             (match(outport = 6) | match(outport = 7)) >> augmented_B >> 
                             (match(outport = 2) | match(outport = 3)))
    disjoint_policies.append((match(inport = 2)| match(inport = 3)) >> augmented_B >> 
                             match(outport = 8) >> augmented_C >> (match(outport = 4)))
    
    disjoint_policies.append((match(inport = 4)) >> augmented_C >> 
                             match(outport = 5) >> augmented_A >> (match(outport = 1))) 
    disjoint_policies.append((match(inport = 4)) >> augmented_C >> 
                             (match(outport = 6) | match(outport = 7)) >> augmented_B >> 
                             (match(outport = 2) | match(outport = 3)))
    disjoint_policies.append((match(inport = 4)) >> augmented_C >> 
                             match(outport = 8) >> augmented_C >> (match(outport = 4)))
    
    composed_policy = disjoint(disjoint_policies, [])
    """
    parallel_total = (augmented_A+augmented_B+augmented_C)
    
    start = time.time()
    flow_rules = parallel_total.compile()
    time_compile = time.time()-start 
    print "Compiling the big parallel to warm up the cache", time_compile, "seconds"
    print flow_rules
    
    composed_policy = (parallel_total >> parallel_total)
    """
    print "Compiling the composed policy to avoid compilation delay"
    start = time.time()
    flow_rules = composed_policy.compile()
    time_compile = time.time()-start
    print "Compiled the composed policy", time_compile,"seconds"
    #print flow_rules
    
    return composed_policy

if __name__ == '__main__':
    print "Running the example"
    sigcomm_example()

