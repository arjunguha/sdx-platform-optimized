#############################################
# Experiment to evaluate the compilation    #
# times for N participants                #
# author: Arpit Gupta (glex.qsd@gmail.com)  #
#############################################
"""
Focusses on testing the initial composition time
with and without compiler-cache implementeds
Here:
ntot participants
nin of them advertising p1,p2,p3,p4,p5,p6 with inbound policies
ntot-nin of them with outbound policies
"""


#
from common import *

           
def main():
    ntot=2
    nin=1  # number of participants with inbound policies
    sdx_participants=generate_sdxglobal(ntot,nin)
    (sdx,participants) = sdx_parse_config('sdx_global.cfg')
    update_paramters(sdx,ntot,nin)
    generate_policies(sdx,participants,ntot,nin)
    aggr_policies=sdx_platform(sdx)
    start_comp=time.time()
    agg_compile=aggr_policies.compile()
    #print "Compiled Result: ",agg_compile
    #compiled_parallel=compileParallel(sdx)
    print  'Completed Aggregate Compilation ',time.time() - start_comp, "seconds"
        
    print "DATA: policy_parl",len(policy_parl)
    #print "DATA: policy_seq ",policy_seq
    #print "Add called ",count_classifierAdd
    print "DATA: add_cache ", len(add_cache)
   

if __name__ == '__main__':
    cProfile.run('main()', 'restats')