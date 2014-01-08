#############################################
# Set Operations on IP Prefixes             #
# author: Arpit Gupta (glex.qsd@gmail.com)  #
#############################################

import cProfile
import setOperation as so
import pstats

cProfile.run('so.main()', 'restats')

p = pstats.Stats('restats')
p.strip_dirs().sort_stats(-1).print_stats()