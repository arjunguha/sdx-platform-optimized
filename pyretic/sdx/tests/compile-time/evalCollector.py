#############################################
# author: Arpit Gupta (glex.qsd@gmail.com)  #
#############################################
"""
Generic script to collect results from various results in new_eval.py
"""

from new_eval import *
import os,json,sys
import subprocess
from multiprocessing import Process, Queue
from time import gmtime, strftime

dataPoints=20
recursionLimit=100000

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
    time_curr=strftime("%a%d%b%Y%H%M%S", gmtime())
    #print time_curr
    dname=option+'_'+str(time_curr)+'.dat'
    
    if option=='prefixBM':
        data={}
        print 'Running Prefix Benchmarking Experiment'

        #modes=['dlsm','lsm','naive']
        #nparts=[20,40,80,160]
        #modes=['dlsm','lsm']
        nparts=[50]
        npfxes=[2000,4000,6000,8000,10000]
        fractionGroup=[0.025,0.05,0.075,0.1]
        #fractionGroup=[0.025]
        #npfx=10
        nfields=1
        mode='dlsm'
        #data['partpfx']=partpfx
        data['npfxes']=npfxes
        data['nfields']=nfields
        data['modes']=mode
        data['fractionGroup']=fractionGroup
        data['time']={}
        data['nvnhs']={} 
        data['mdsTime']={}
        data['augmentTime']={}       
        for npfx in npfxes:
            ntot=nparts[0]
            k1=npfx
            data['nvnhs'][k1]={}
            data['mdsTime'][k1]={}
            data['augmentTime'][k1]={}
            for fg in fractionGroup:
                k2=fg
                data['nvnhs'][k1][k2]=[]
                data['mdsTime'][k1][k2]=[]
                data['augmentTime'][k1][k2]=[]
                
                for dp in range(dataPoints):
                    print "iteration: ",dp+1
                    q=Queue()
                    p=Process(target=prefixGroupExperiment, args=(mode,ntot,npfx,nfields,fg,q))
                    p.start()
                    qout=q.get()
                    p.join()
                    augmentTime,mdsTime,nVNHs=qout
                    data['nvnhs'][k1][k2].append(nVNHs)
                    data['mdsTime'][k1][k2].append(mdsTime)
                    data['augmentTime'][k1][k2].append(augmentTime)
                    
        with open(dname, 'w') as outfile:
            json.dump(data,outfile,ensure_ascii=True,encoding="ascii")          
        print data
        
    elif option=='compileTime':
        data={}
        print 'Running Compilation Time Experiment'

        #modes=['dlsm','lsm','naive']
        #nparts=[20,40,80,160]
        #modes=['dlsm','lsm']
        nparts=[100,200,300,400]
        npfxes=[2500,5000,7500,10000]
        #fractionGroup=[0.025,0.05,0.075,0.1]
        fractionGroup=[0.005]
        #npfx=10
        nfields=1
        mode='dlsm'
        #data['partpfx']=partpfx
        data['nparts']=nparts
        data['npfxes']=npfxes
        data['nfields']=nfields
        data['modes']=mode
        data['fractionGroup']=fractionGroup
        data['cTime']={}
        data['nrules']={}
        data['nvnhs']={} 
        data['mdsTime']={}
        data['augmentTime']={}       
        for ntot in nparts:
            #ntot=nparts[0]
            fg=fractionGroup[0]
            k1=ntot
            data['nvnhs'][k1]={}
            data['mdsTime'][k1]={}
            data['augmentTime'][k1]={}
            data['cTime'][k1]={}
            data['nrules'][k1]={}
            for npfx in npfxes:
                k2=npfx
                data['nvnhs'][k1][k2]=[]
                data['mdsTime'][k1][k2]=[]
                data['augmentTime'][k1][k2]=[]
                data['cTime'][k1][k2]=[]
                data['nrules'][k1][k2]=[]
                
                for dp in range(dataPoints):
                    print "iteration: ",dp+1
                    q=Queue()
                    p=Process(target=compilationTimeExperiment, args=(mode,ntot,npfx,nfields,fg,q))
                    p.start()
                    qout=q.get()
                    p.join()
                    augmentTime,mdsTime,nVNHs,nRules,compileTime=qout
                    data['nvnhs'][k1][k2].append(nVNHs)
                    data['mdsTime'][k1][k2].append(mdsTime)
                    data['augmentTime'][k1][k2].append(augmentTime)
                    data['cTime'][k1][k2].append(compileTime)
                    data['nrules'][k1][k2].append(nRules)
                    
        with open(dname, 'w') as outfile:
            json.dump(data,outfile,ensure_ascii=True,encoding="ascii")          
        print data
        
        
        
    elif option=='MDS':
        data={}
        print 'Running Prefix Benchmarking Experiment'

        #modes=['dlsm','lsm','naive']
        #nparts=[20,40,80,160]
        #modes=['dlsm','lsm']
        nparts=[100,200,300,400,500]
        npfxes=[2500,5000,7500,10000]
        #fractionGroup=[0.025,0.05,0.075,0.1]
        fractionGroup=[0.01]
        #npfx=10
        nfields=1
        mode='dlsm'
        #data['partpfx']=partpfx
        data['nparts']=nparts
        data['npfxes']=npfxes
        data['nfields']=nfields
        data['modes']=mode
        data['fractionGroup']=fractionGroup
        data['time']={}
        data['nvnhs']={} 
        data['mdsTime']={}
        data['augmentTime']={}       
        for ntot in nparts:
            #ntot=nparts[0]
            fg=fractionGroup[0]
            k1=ntot
            data['nvnhs'][k1]={}
            data['mdsTime'][k1]={}
            data['augmentTime'][k1]={}
            for npfx in npfxes:
                k2=npfx
                data['nvnhs'][k1][k2]=[]
                data['mdsTime'][k1][k2]=[]
                data['augmentTime'][k1][k2]=[]
                
                for dp in range(dataPoints):
                    print "iteration: ",dp+1
                    q=Queue()
                    p=Process(target=prefixGroupExperiment, args=(mode,ntot,npfx,nfields,fg,q))
                    p.start()
                    qout=q.get()
                    p.join()
                    augmentTime,mdsTime,nVNHs=qout
                    data['nvnhs'][k1][k2].append(nVNHs)
                    data['mdsTime'][k1][k2].append(mdsTime)
                    data['augmentTime'][k1][k2].append(augmentTime)
                    
        with open(dname, 'w') as outfile:
            json.dump(data,outfile,ensure_ascii=True,encoding="ascii")          
        print data
        
    send_email(option)
        
if __name__ == '__main__':
    sys.setrecursionlimit(recursionLimit)
    main(sys.argv[1])  
    