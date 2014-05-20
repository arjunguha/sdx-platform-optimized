#############################################
# author: Arpit Gupta (glex.qsd@gmail.com)  #
#############################################


import sys, getopt
import mininet
from mininet.topo import SingleSwitchTopo
from mininet.net import Mininet
from mininet.log import setLogLevel
from mininet.node import RemoteController
from mininet.cli import CLI

def getArgs():
    cli = False;
    controller = '127.0.0.1'
    
    try:
        opts, args = getopt.getopt(sys.argv[1:],"h",["help", "cli", "controller="])
    except getopt.GetoptError:
        print 'sdx_mininet_simple.py [--cli --controller <ip address>]'
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            
            print 'sdx_mininet_simple.py [--cli --controller <ip address>]'
            sys.exit()
        elif opt == '--cli':
            cli = True
        elif opt == '--controller':
            controller = arg
    return (cli, controller)
   
def simple(cli, controllerIP):
    "Create and test SDX Simple Module"
    print "Creating the topology with one IXP switch and three participating ASs\n\n" 
    topo = SingleSwitchTopo(k=4)
    net = Mininet(topo, controller=lambda name: RemoteController( 'c0', controllerIP ), autoSetMacs=True) #, autoStaticArp=True)
    net.start()
    hosts=net.hosts
    print "Configuring participating ASs\n\n"
    for host in hosts:
        if host.name=='h1':
            # Interface configuration
            print "configuring h1"
            host.cmdPrint('sudo ifconfig h1-eth0:0 66.66.0.1/16 up')
            host.cmdPrint('sudo ifconfig h1-eth0:1 100.0.5.1/24 up')
            host.cmdPrint('sudo ifconfig h1-eth0:2 130.0.0.1/24 up')   
            host.cmdPrint('sudo ifconfig -a')        
            # Route configuration
            host.cmd('sudo ip route add 100.0.1.0/24 via 66.66.0.4 dev eth0')
            host.cmd('sudo ip route add 100.0.2.0/24 via 66.66.0.4 dev eth0')
            host.cmd('sudo ip route add 100.0.3.0/24 via 66.66.0.2 dev eth0')
            host.cmd('sudo ip route add 100.0.4.0/24 via 66.66.0.4 dev eth0')
            host.cmdPrint('sudo route -n')

        if host.name=='h2':
            # Interface configuration
            print "configuring h2"
            host.cmd('sudo ifconfig h2-eth0:0 66.66.0.2/16 up')
            host.cmd('sudo ifconfig h2-eth0:1 100.0.1.1/24 up')
            host.cmd('sudo ifconfig h2-eth0:2 100.0.2.1/24 up')
            host.cmd('sudo ifconfig h2-eth0:3 100.0.3.1/24 up')
            host.cmd('sudo ifconfig h2-eth0:4 100.0.4.1/24 up')
            host.cmdPrint('sudo ifconfig -a')            
            # Route configuration            
            host.cmd('sudo ip route add 100.0.5.0/24 via 66.66.0.1 dev eth0')
            host.cmd('sudo ip route add 130.0.0.0/24 via 66.66.0.1 dev eth0')
            host.cmdPrint('sudo route -n')
        
        if host.name=='h3':
            # Interface configuration
            print "configuring h3"
            host.cmd('sudo ifconfig h3-eth0:0 66.66.0.3/16 up')
            host.cmd('sudo ifconfig h3-eth0:1 100.0.1.1/24 up')
            host.cmd('sudo ifconfig h3-eth0:2 100.0.2.1/24 up')
            host.cmd('sudo ifconfig h3-eth0:3 100.0.3.1/24 up')
            host.cmd('sudo ifconfig h3-eth0:4 100.0.4.1/24 up') 
            host.cmdPrint('sudo ifconfig -a')          
            # Route configuration            
            host.cmd('sudo ip route add 100.0.5.0/24 via 66.66.0.1 dev eth0')
            host.cmd('sudo ip route add 130.0.0.0/24 via 66.66.0.1 dev eth0')
            host.cmdPrint('sudo route -n')
        
        if host.name=='h4':
            # Interface configuration
            print "configuring h4"
            host.cmd('sudo ifconfig eth0:0 66.66.0.4/16 up')
            host.cmd('sudo ifconfig h4-eth0:1 100.0.1.1/24 up')
            host.cmd('sudo ifconfig h4-eth0:2 100.0.2.1/24 up')
            host.cmd('sudo ifconfig h4-eth0:3 100.0.3.1/24 up')
            host.cmd('sudo ifconfig h4-eth0:4 100.0.4.1/24 up') 
            host.cmdPrint('sudo ifconfig -a')          
            # Route configuration            
            host.cmd('sudo ip route add 100.0.5.0/24 via 66.66.0.1 dev eth0')
            host.cmd('sudo ip route add 130.0.0.0/24 via 66.66.0.1 dev eth0')
            host.cmdPrint('sudo route -n')
    if (cli): # Running CLI
        CLI(net)
    else:
        print "Running the Ping Tests\n\n"
        for host in hosts:
            if host.name=='h1':
                host.cmdPrint('ping -c 5 -I 100.0.5.1 100.0.1.1')
            
    net.stop()
    print "\n\nExperiment Complete !\n\n"

if __name__ == '__main__':
    # Tell mininet to print useful information
    setLogLevel('info')
    # Parse arguments
    (cli, controller) = getArgs() 
    
    simple(cli, controller) 