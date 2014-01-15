#############################################
# author: Arpit Gupta (glex.qsd@gmail.com)  #
#############################################
"""
Generic benchmarking data collection script
"""

from predicateBM import *
import os,json,sys
import subprocess
from multiprocessing import Process, Queue

dataPoints=2

def getKey(ntot,npfx):
    return str(ntot)+","+str(npfx)

def send_email():
    import smtplib

    gmail_user = "glex.qsd@gmail.com"
    gmail_pwd = "****"
    FROM = 'glex.qsd@@gmail.com'
    TO = ['glex.qsd@gmail.com'] #must be a list
    SUBJECT = "SDX: Predicate Benchmarking results"
    TEXT = "Completed Predicate Benchmarking."

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
        #server.quit()
        server.close()
        print 'successfully sent the mail'
    except:
        print "failed to send mail"
    
def main(option):
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
                    
        with open('predicateBM.dat', 'w') as outfile:
            json.dump(data,outfile,ensure_ascii=True,encoding="ascii")          
        print data
        send_email()
        
if __name__ == '__main__':
    main(sys.argv[1])  
    