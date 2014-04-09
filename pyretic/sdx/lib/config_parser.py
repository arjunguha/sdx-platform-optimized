#############################################
# Configuration parser                      #
# author: Arpit Gupta (glex.qsd@gmail.com)  #
#############################################


import json
from pyretic.sdx.lib.corelib import *


def sdx_parse_config(config_file):
    sdx = SDX()
    
    sdx_config = json.load(open(config_file, 'r'))
    #print sdx_config
    sdx_ports = {}
    sdx_vports = {}
    
    ''' 
        Create SDX environment ...
    '''
    for participant_name in sdx_config:
        
        ''' Adding physical ports '''
        participant = sdx_config[participant_name]
        sdx_ports[participant_name] = [PhysicalPort(id_=participant["Ports"][i]['Id'],mac=MAC(participant["Ports"][i]["MAC"]),ip=IP(participant["Ports"][i]["IP"])) for i in range(0, len(participant["Ports"]))]     
        print sdx_ports[participant_name]
        ''' Adding virtual port '''
        sdx_vports[participant_name] = VirtualPort(participant=participant_name) #Check if we need to add a MAC here
    
    sdx.sdx_ports=sdx_ports   
    for participant_name in sdx_config:
        peers = {}
        
        ''' Assign peers to each participant '''
        for peer_name in sdx_config[participant_name]["Peers"]:
            peers[peer_name] = sdx_vports[peer_name]
            
        ''' Creating a participant object '''
        sdx_participant = SDXParticipant(id_=participant_name,vport=sdx_vports[participant_name],phys_ports=sdx_ports[participant_name],peers=peers)
        
        ''' Adding the participant in the SDX '''
        sdx.add_participant(sdx_participant,participant_name)
    
    return sdx

if __name__ == '__main__':
    sdx_parse_config('/home/sdx/pyretic-fork/pyretic/pyretic/sdx/sdx_global.cfg')
    