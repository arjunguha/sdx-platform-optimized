"""
     SDX Runtime
     Author: Arpit Gupta (glex.qsd@gmail.com), Muhammad Shahbaz, Laurent Vanbever
"""

## General imports
import os
from threading import Thread,Event
from multiprocessing import Process,Queue

## SDX-specific imports
from pyretic.sdx.utils import *
from pyretic.sdx.utils.arp import *
from pyretic.sdx.utils.inet import *
from pyretic.sdx.bgp.route_server import route_server
from pyretic.sdx.lib.corelib import *
from pyretic.sdx.lib.config_parser import *
from pyretic.sdx.lib.policy_parser import *
from pyretic.sdx.lib.composition import *
from pyretic.sdx.lib.compilation import *


# Generate SDX configuration automatically
auto=False

class SDXPolicy(DynamicPolicy):
    """Standard MAC-learning logic"""
    def __init__(self):       

        """Initialize SDX policies as dynamic"""
        print "Initialize SDX"
        super(SDXPolicy,self).__init__()        
        
        #print "SDX:",self.__dict__        
        

class Runtime():
    def __init__(self,arp_policy):
        self.arp_policy = arp_policy
        sdxPolicy = SDXPolicy()
        self.policy=sdxPolicy
        cwd = os.getcwd()
        sdx_autoconf=cwd+'/pyretic/sdx/sdx_auto.cfg'
        self.sdx = sdx_parse_config(cwd+'/pyretic/sdx/sdx_global.cfg',sdx_autoconf,auto)
        print "config parser completed "
        
        ''' Event handling for dynamic policy compilation '''  
        event_queue = Queue()
        ready_queue = Queue()
        
        ''' Dynamic update policy thread '''
        dynamic_update_policy_thread = Thread(target=dynamic_update_policy_event_hadler, args=(event_queue,ready_queue, self.update_policy))
        dynamic_update_policy_thread.daemon = True
        dynamic_update_policy_thread.start()   
        
        ''' Router Server interface thread '''
        # TODO: confirm if we need RIBs per participant or per peer!
        rs = route_server(event_queue, ready_queue, self.sdx)        
        rs_thread = Thread(target=rs.start)
        rs_thread.daemon = True
        rs_thread.start()
        
        ''' Update policies'''
        event_queue.put("init")
        #TODO: Should we send the loaded routes on bootup to the participants?

        
    def update_policy(self,event_source='init'):
        
        cwd = os.getcwd()
        
        print "Calling policy parser"
        sdx_parse_policies(cwd+'/pyretic/sdx/sdx_policies.cfg',self.sdx,event_source)
        
        ''' Get updated policy '''
        self.policy = sdx_platform(self.sdx)
        
        #print 'Final Policy'
        #print self.policy
        
        ''' Get updated IP to MAC list '''
        # TODO: Maybe we won't have to update it that often - MS
        #       Need efficient implementation of this ...
        self.arp_policy.mac_of = get_ip_mac_list(self.sdx.VNH_2_IP,self.sdx.VNH_2_MAC)
        
        
        #print 'Updated ARP Policy'
        #print self.arp_policy
        

'''' Dynamic update policy handler '''
def dynamic_update_policy_event_hadler(event_queue,ready_queue,update_policy):    
    while True:
        event_source=event_queue.get()        
        ''' Compile updates '''
        update_policy(event_source)        
        if ('bgp' in event_source):
            ready_queue.put(event_source)
