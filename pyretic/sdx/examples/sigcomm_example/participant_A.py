
import json
import os
from pyretic.sdx.lib.corelib import *


cwd = os.getcwd()


def policy(participant, sdx):
    '''
        Specify participant policy
        match(dstport = 80) >> fwd(B)
    '''
    #prefixes_announced=bgp_get_announced_routes(sdx,'1')

    final_policy= (
                   (match(dstport = 80) >> sdx.fwd(participant.peers['B'])) +
                   (match(dstport = 443) >> sdx.fwd(participant.peers['C']))
                  )            
    return final_policy