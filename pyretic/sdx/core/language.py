"""
 Language extension to match for prefix sets in Pyretic                           
"""

from pyretic.sdx.core.pyreticlib import *

class match_prefixes_set(DerivedPolicy, Filter):
    """ Maintain a set of IP prefixes.
        Only useful in the first stages of the SDX compilation."""
    def __init__(self, pfxes):
        
        if isinstance(pfxes, set):
            self.pfxes = pfxes
        else:
            self.pfxes = set(pfxes)
        super(match_prefixes_set, self).__init__(passthrough)
    
    def __repr__(self):
        return "match_prefix_set:\n%s" % util.repr_plus([self.pfxes])