#############################################
# author: Arpit Gupta (glex.qsd@gmail.com)  #
#############################################
"""
Generic benchmarking data collection script
"""

from predicateBM import *
from composePolicy import *
import os,json,sys
import subprocess
from multiprocessing import Process, Queue

dataPoints=2

def getKey(ntot,npfx):
    return str(ntot)+","+str(npfx)

def send_email(option):
    import smtplib
    import datetime
    current_time = datetime.datetime.now().time()

    gmail_user = "glex.qsd@gmail.com"
    gmail_pwd = "****"
    FROM = 'glex.qsd@@gmail.com'
    TO = ['glex.qsd@gmail.com'] #must be a list
    
    SUBJECT = "SDX: "+str(option).upper()+" Benchmarking results"
    TEXT = "Completed "+str(option).upper()+" Benchmarking at: "+str(current_time)

    # Prepare actual message
    message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
            """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
        
    # Try sending the email
    try:
        #server = smtplib.SMTP(SERVER) 
        server = smtplib.SMTP("smtp.gmail.com", 587) #or port 465 doesn't seem to work!
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        server.sendmail(FROM, TO, message)
        server.close()
        print 'successfully sent the mail'
    except:
        print "failed to send mail"
    
def main(option):
    dname=option+'BM.dat'+time.time()
    if option=='predicate':
        data={}
        print 'Running Predicate Experiment'
        # number of participants and prefix groups
        #partpfx=[(20,50),(40,100),(100,100)]
        partpfx=[(10,5),(10,10)]
        # header fields
        nheaders=range(4)
        #data['partpfx']=partpfx
        data['time']={}
        data['space']={}        
        for ntot,npfx in partpfx:
            k=getKey(ntot,npfx)
            data['time'][k]={}
            data['space'][k]={}
            for nfields in nheaders:
                
                data['time'][k][nfields]=[]
                data['space'][k][nfields]=[]
                for dp in range(dataPoints):
                    print "iteration: ",dp+1
                    q=Queue()
                    p=Process(target=experiment, args=(ntot,npfx,nfields,q))
                    p.start()
                    qout=q.get()
                    p.join()
                    nRules,compileTime=qout
                    #nRules,compileTime=experiment(ntot,npfx,nfields)
                    data['time'][k][nfields].append(compileTime)
                    data['space'][k][nfields].append(nRules)
                 
        with open(dname, 'w') as outfile:
            json.dump(data,outfile,ensure_ascii=True,encoding="ascii")          
        print data
        
    elif option=='compose':
        data={}
        print 'Running Policy Composition Experiment'

        #modes=['dlsm','lsm','naive']
        #nparts=[20,40,80,160]
        modes=['dlsm','lsm']
        nparts=[20,40,80,160]
        
        npfx=10
        nfields=1

        #data['partpfx']=partpfx
        data['modes']=modes
        data['nfields']=nfields
        data['npfx']=npfx
        data['time']={}
        data['space']={}        
        for mode in modes:
            k=mode
            data['time'][k]={}
            data['space'][k]={}
            for ntot in nparts:                
                data['time'][k][ntot]=[]
                data['space'][k][ntot]=[]
                for dp in range(dataPoints):
                    print "iteration: ",dp+1
                    q=Queue()
                    p=Process(target=composeExperiment, args=(mode,ntot,npfx,nfields,q))
                    p.start()
                    qout=q.get()
                    p.join()
                    nRules,compileTime=qout
                    #nRules,compileTime=experiment(ntot,npfx,nfields)
                    data['time'][k][ntot].append(compileTime)
                    data['space'][k][ntot].append(nRules)
                    
        with open(dname, 'w') as outfile:
            json.dump(data,outfile,ensure_ascii=True,encoding="ascii")          
        print data
    elif option=='pgroup':
        data={}
        print 'Running Prefix group Experiment'

        #modes=['dlsm','lsm','naive']
        #nparts=[20,40,80,160]
        #modes=['dlsm','lsm']
        nparts=[50]
        npfxes=[200,400,600]
        #npfx=10
        nfields=1
        mode='dlsm'
        #data['partpfx']=partpfx
        data['npfxes']=npfxes
        data['nfields']=nfields
        data['modes']=mode
        data['time']={}
        data['space']={}        
        for ntot in nparts:
            k=ntot
            data['time'][k]={}
            data['space'][k]={}
            for npfx in npfxes:                
                data['time'][k][npfx]=[]
                data['space'][k][npfx]=[]
                for dp in range(dataPoints):
                    print "iteration: ",dp+1
                    q=Queue()
                    p=Process(target=composeExperiment, args=(mode,ntot,npfx,nfields,q))
                    p.start()
                    qout=q.get()
                    p.join()
                    nRules,compileTime=qout
                    #nRules,compileTime=experiment(ntot,npfx,nfields)
                    data['time'][k][npfx].append(compileTime)
                    data['space'][k][npfx].append(nRules)
                    
        with open(dname, 'w') as outfile:
            json.dump(data,outfile,ensure_ascii=True,encoding="ascii")          
        print data
        
        
    send_email(option)
        
if __name__ == '__main__':
    main(sys.argv[1])  
    