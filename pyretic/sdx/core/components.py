
from pyretic.sdx.core.pyreticlib import *

"""
    SDX Platform's Components
        -Physical Ports
        -Virtual Ports
        -SDX Participants
"""


class Port(object):
    """Represents a switch port"""
    def __init__(self, mac='', participant=None, ip=''):
        self.mac = mac
        self.participant = participant
        self.ip = ip
        
        
class PhysicalPort(Port):
    """Abstract class that represents a physical port"""
    def __init__(self, id_, *args, **kwargs):
        super(PhysicalPort, self).__init__(*args, **kwargs)
        self.id_ = id_


class VirtualPort(Port):
    """Abstract class that represents a virtual port"""
    def __init__(self, *args, **kwargs):
        super(VirtualPort, self).__init__(*args, **kwargs)


class SDXParticipant(object):
    """Represent a particular SDX participant"""
    def __init__(self, id_, vport, phys_ports, peers={}, policies=None, rs_client=None, custom_routes=[]):
        self.id_ = id_
        self.vport = vport
        self.phys_ports = phys_ports
        self.peers = peers
        self.policies = policies
        self.original_policies = None       
        self.vport.participant = self  # set the participant
        self.n_policies = 0
        self.rs_client = rs_client
        self.custom_routes = custom_routes
    
    def init_policy(self, new_policy):
        self.policies = new_policy
        self.n_policies = 1
        
    def add_policy(self, new_policy):
        self.policies = parallel([self.policies, new_policy])
        self.n_policies += 1

        
if __name__ == '__main__':
    vport = VirtualPort()
    pport = PhysicalPort(id_=1)
    sdxpart = SDXParticipant(1, vport, pport)
    print sdxpart.id_