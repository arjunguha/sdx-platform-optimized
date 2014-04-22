"""
    Parser to configure SDX platform
    Author: Arpit Gupta, Laurent Vanbever
"""


import json
import random
#from netaddr import *

from pyretic.sdx.lib.corelib import *


def getPeering(ratio):
    """
        getPeering(ratio)=0/1
    """
    if random.random()<ratio:
        return 1
    else:
        return 0

    
def generatePeeringMatrix(n,ratio):
    pm=[]
    for row in range(n):
        pm.append([])
        for col in range(n):
            if row!=col:
                pm[row].append(getPeering(ratio))
            else:
                pm[row].append(1)
            if row==0 or col==0:
                pm[row].append(1)
    return pm


def getNports(ntot,portDistr,ind):
    frac=float(ind)/float(ntot)
    sum=float(portDistr.values()[0])
    for i in portDistr.keys():
        if frac<=sum:
            return int(i)
        else:
            sum+=float(portDistr[i])           


def generate_sdxglobal(ntot,portDistr,peeringMatrix,iplist,macinit):
    sdx_participants={}
    for ind in range(1,ntot+1):
        peers=[]
        for i in filter(lambda x:(x!=ind)& (peeringMatrix[ind-1][x-1]!=0),range(1,ntot+1)):
            peers.append(str(i))
        
        #print ind,peers
        
        ports=[]
        nports=getNports(ntot,portDistr,ind)
        #print ind,nports        
        for i in range(nports):
            # TODO: Get mac-addresses for physical ports from MiniNExT?  
            count = ind if i==0 else (ind*ntot+i)
            ip,mac=str(iplist[count]),str(EUI(int(EUI(macinit))+count))
            ports.append({'Id':count,'MAC':mac,'IP':ip})                   
                
        sdx_participants[ind]={'Ports':ports,'Peers':peers}
        
    return sdx_participants


def automate_config(config_file,sdx_autoconf):
    """
        Automate Generation of SDX configuration (useful for MiniNExT emulation)
    """
    autoconf = json.load(open(sdx_autoconf, 'r'))
    
    # Get the parameters from auto-config file
    ntot=autoconf['ntot']
    portDistr=autoconf['portDistr']
    peeringRatio = autoconf['peeringRatio']
    iplist=list(IPNetwork(autoconf['subnet']))
    macinit=autoconf['macinit']
    
    # Generate the Peering Matrix
    peeringMatrix = generatePeeringMatrix(ntot,peeringRatio)
    
    sdx_participants = generate_sdxglobal(ntot,portDistr,peeringMatrix,iplist,macinit)
    
    # Update the sdx global config file
    with open(config_file, 'w') as outfile:
        json.dump(sdx_participants,outfile,ensure_ascii=True)
        
    return iplist,macinit


def update_params(sdx,iplist,macinit):
    participant_2_port = {}
    port_2_participant = {}
    
    for participant in sdx.participants.values():        
        participant_2_port[participant.id_]={}
        participant_2_port[participant.id_][participant.id_]=[participant.phys_ports[i].id_ 
                                                              for i in range(len(participant.phys_ports))]
        for phyport in participant.phys_ports:
            port_2_participant[phyport.id_]=participant.id_
        for peer in participant.peers:
            participant_2_port[participant.id_][peer]=[participant.peers[peer].participant.phys_ports[0].id_]
            
    sdx.participant_2_port = participant_2_port
    sdx.port_2_participant = port_2_participant
    
    """ Update the VNH parameters"""
    sdx.VNH_2_IP['VNH'] = iplist
    sdx.VNH_2_MAC['VNH'] = macinit


def sdx_parse_config(config_file,sdx_autoconf,auto):
    """
        Parse SDX configuration
    """
    if auto:
        iplist,macinit=automate_config(config_file,sdx_autoconf)
    else:
        autoconf = json.load(open(sdx_autoconf, 'r'))
        iplist=list(IPNetwork(autoconf['subnet']))
        macinit=autoconf['macinit']
        
    sdx = SDX()
    sdx_config = json.load(open(config_file, 'r'))
    sdx_ports = {}
    sdx_vports = {}
    
    ''' 
        Create SDX environment ...
    '''
    for participant_name in sdx_config:
        
        ''' Adding physical ports '''
        participant = sdx_config[participant_name]
        sdx_ports[participant_name] = [PhysicalPort(id_=participant["Ports"][i]['Id'],mac=MAC(participant["Ports"][i]["MAC"]),ip=IP(participant["Ports"][i]["IP"])) for i in range(0, len(participant["Ports"]))]     
        
        ''' Adding virtual port '''
        sdx_vports[participant_name] = VirtualPort(participant=participant_name) #Check if we need to add a MAC here
        
        #print sdx_ports[participant_name], sdx_vports[participant_name].participant
    
    sdx.sdx_ports = sdx_ports 
    sdx.sdx_vports = sdx_vports
    
    for participant_name in sdx_config:
        peers = {}
        
        ''' Assign peers to each participant '''
        for peer_name in sdx_config[participant_name]["Peers"]:
            peers[peer_name] = sdx_vports[peer_name]
            
        ''' Creating a participant object '''
        sdx_participant = SDXParticipant(id_=participant_name,vport=sdx_vports[participant_name],phys_ports=sdx_ports[participant_name],peers=peers)
        
        ''' Adding the participant in the SDX '''
        sdx.add_participant(sdx_participant,participant_name)
    
    ''' Update other SDX platform params like port_2_participant, participant_2_port etc..'''
    update_params(sdx,iplist,macinit)    
    
    return sdx


if __name__ == '__main__':
    sdx_parse_config('/home/sdx/pyretic-fork/pyretic/pyretic/sdx/sdx_global.cfg','/home/sdx/pyretic-fork/pyretic/pyretic/sdx/sdx_auto.cfg',True)

    