#############################################
# author: Arpit Gupta (glex.qsd@gmail.com)  #
#############################################
"""
Plotting figures for SIGCOMM'14
"""
sigdir='/Users/glex/Documents/writings/sdx/sdx/doc/sigcomm14'
import os, sys, json
fig2data={'MDS-pg':'mdsTrace_Wed29Jan2014195955.dat','initCompile':'UPDATEDcompileTime_Wed29Jan2014023720.dat',
          'bgpUpdateCDF':'bgpUpdate_Wed29Jan2014062818.dat','bgpUpdate':'bgpUpdate_Wed29Jan2014031457.dat',
          'MDS-amsix':'mdsTrace_Wed29Jan2014195955.dat'}

figlist=['MDS-pg_nvnhs.eps','MDS-pg_nvnhs.eps','MDS-pg_nvnhs.eps','MDS-pg_nvnhs.eps',
         'MDS-pg_nvnhs.eps','MDS-pg_nvnhs.eps']
# Generate all the results    
for exp in fig2data:
    os.system('python plotEval.py '+exp)

# Send the results to sigcomm directory
