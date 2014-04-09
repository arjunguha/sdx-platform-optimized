#############################################
# Configuration parser                      #
# author: Arpit Gupta (glex.qsd@gmail.com)  #
#############################################


from pyretic.sdx.lib.corelib import *
from pyretic.sdx.sdxlib import *
from pyretic.sdx.lib.config_parser import *
from importlib import import_module

def sdx_parse_policies(policy_file,sdx):
        
    sdx_policies = json.load(open(policy_file,'r'))  
    ''' 
        Get participants policies
    '''
    for participant_name in sdx_policies:
        participant = sdx.participants[participant_name]
        policy_modules = [import_module(sdx_policies[participant_name][i]) 
                          for i in range(0, len(sdx_policies[participant_name]))]
        
        participant.policies = parallel([
             policy_modules[i].policy(participant, sdx) 
             for i in range(0, len(sdx_policies[participant_name]))])  
        print "Before pre",participant.policies
        # translate these policies for VNH Assignment
        participant.original_policies=participant.policies
        participant.policies=pre_VNH(participant.policies,sdx,participant_name,participant)
        
        print "After pre: ",participant.policies
    #print sdx.out_var_to_port[u'outB_1'].id_  
       
    # Virtual Next Hop Assignment
    vnh_assignment(sdx) 
    print "Completed VNH Assignment"
    # translate these policies post VNH Assignment
    
    classifier=[]
    for participant_name in sdx.participants:
        sdx.participants[participant_name].policies=post_VNH(sdx.participants[participant_name].policies,
                                                         sdx,participant_name)        
        print "After Post VNH: ",sdx.participants[participant_name].policies
        start_comp=time.time()
        classifier.append(sdx.participants[participant_name].policies.compile())
        print participant_name, time.time() - start_comp, "seconds"


def sdx_parse_announcements(announcement_file,sdx):
        
    sdx_announcements = json.load(open(announcement_file,'r'))  
    ''' 
        Get participants custom routes
    '''
    for participant_name in sdx_announcements:
        participant = sdx.participants[participant_name]
        announcement_modules = [import_module(sdx_announcements[participant_name][i]) 
                          for i in range(0, len(sdx_announcements[participant_name]))]
        
        participant.custom_routes = []
        for announcement_module in announcement_modules:
            participant.custom_routes.extend(announcement_module.custom_routes(participant,sdx))
        
def sdx_annouce_custom_routes(sdx):
    ''' 
        Announce participants custom routes
    '''    
    for participant_name in sdx.participants:
        for route in sdx.participants[participant_name].custom_routes:
            bgp_announce_route(sdx,route)

if __name__ == '__main__':
    # TODO: Write better unit test for this function
    sdx= sdx_parse_config('/home/sdx/pyretic-fork/pyretic/pyretic/sdx/sdx_global.cfg')
    sdx_parse_policies('/home/sdx/pyretic-fork/pyretic/pyretic/sdx/sdx_policies.cfg',sdx)