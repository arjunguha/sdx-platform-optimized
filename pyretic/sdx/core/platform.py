"""
    SDX Platform
    Author: Arpit Gupta (glex.qsd@gmail.com), Muhammad Shahbaz, Laurent Vanbever
"""

from netaddr import *

## Pyretic-specific imports
from pyretic.sdx.core.pyreticlib import *
from pyretic.sdx.core.components import *


###
### SDX classes
###

class SDX(object):
    """Represent a SDX platform class"""
    def __init__(self):
        self.server = None
        
        self.participants = {}
        
        self.sdx_ports={}
        self.sdx_vports={}
        self.participant_id_to_in_var = {}
        self.out_var_to_port = {}
        self.port_id_to_out_var = {}        
        self.participant_2_port={}

        
        VNH_2_pfx = None
        self.VNH_2_IP={}
        self.VNH_2_MAC={}
        self.part_2_VNH={}
        
        self.port_2_participant={}
        self.part_2_prefix_old={}
        self.part_2_prefix_lcs={}
        self.lcs_old=[]
        
    ''' Get the name of the participant belonging to the IP address '''
    def get_participant_name(self,ip):
        
        for participant_name in self.sdx_ports:
            for port in self.sdx_ports[participant_name]:  
                if ip is str(port.ip):
                    return participant_name
    
    def get_neighborList(self,sname):
        #print type(sname)
        neighbor_list=[]
        for participant in self.participants:
            #print participant.peers.keys()
            if sname in self.participants[participant].peers.keys():
                #print "Neighbor found",participant.id_
                neighbor_list.append(self.participants[participant].id_) 
        return neighbor_list
    
    def add_participant(self, participant, name):
        self.participants[name] = participant
        self.participant_id_to_in_var[participant.id_] = "in" + participant.id_.upper()
        i = 0
        for port in participant.phys_ports:
            self.port_id_to_out_var[port.id_] = "out" + participant.id_.upper() + "_" + str(i)
            self.out_var_to_port["out" + participant.id_.upper() + "_" + str(i)] = port
            i += 1
    
    def fwd(self, port):
        if isinstance(port, PhysicalPort):
            return modify(state=self.port_id_to_out_var[port.id_], dstmac=port.mac)
        else:
            return modify(state=self.participant_id_to_in_var[port.participant.id_])


if __name__ == '__main__':
    sdx=SDX()
    print sdx.participant_2_port 
