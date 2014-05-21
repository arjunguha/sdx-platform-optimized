
import json
import os
from pyretic.sdx.lib.corelib import *


cwd = os.getcwd()


def policy(participant, sdx):
    '''
        Specify participant policy
        default forwarding
    '''
    #prefixes_announced=bgp_get_announced_routes(sdx,'1')

    final_policy= (
                   identity
                  )            
    
    return final_policy