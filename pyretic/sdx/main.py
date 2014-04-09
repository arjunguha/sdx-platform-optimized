################################################################################
#
#  <website link>
#
#  File:
#        main.py
#
#  Project:
#        Software Defined Exchange (SDX)
#
#  Author:
#        Arpit Gupta (glex.qsd@gmail.com)
#        Muhammad Shahbaz
#        Laurent Vanbever
#
#  Copyright notice:
#        Copyright (C) 2012, 2013 Georgia Institute of Technology
#              Network Operations and Internet Security Lab
#
#  License:
#        This file is part of the SDX development base package.
#
#        This file is free code: you can redistribute it and/or modify it under
#        the terms of the GNU Lesser General Public License version 2.1 as
#        published by the Free Software Foundation.
#
#        This package is distributed in the hope that it will be useful, but
#        WITHOUT ANY WARRANTY; without even the implied warranty of
#        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#        Lesser General Public License for more details.
#
#        You should have received a copy of the GNU Lesser General Public
#        License along with the SDX source package.  If not, see
#        http://www.gnu.org/licenses/.
#


## SDX-specific imports
from pyretic.sdx.utils import *
from pyretic.sdx.utils.arp import *
from pyretic.sdx.utils.inet import *
from pyretic.sdx.lib.corelib import *
from pyretic.sdx.sdxlib import *


''' Get current working directory ''' 
cwd = os.getcwd()

        
''' Main '''
def main():
    
    arp_policy = arp()        
    runtime=Runtime(arp_policy)
    policy=runtime.policy 
    
    print "SDX policy ",policy    
    
    return if_(ARP,
                   arp_policy,
                   if_(BGP,
                           identity,
                           policy
                   )
               ) >> mac_learner()
               

if __name__ == '__main__':
    main()