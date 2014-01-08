#############################################
# Set Operations on IP Prefixes             #
# author: Arpit Gupta (glex.qsd@gmail.com)  #
#############################################
import os,sys
from multiprocessing import Process, Queue
import multiprocessing as mp
import cProfile
multiprocess=True

debug=False

def get_pset(plist):
    pset=[]
    for elem in plist:
        pset.append(frozenset(elem))
    return set(pset)


def get_pdict(part_2_prefix):
    temp=set()
    for part in part_2_prefix:
        for plist in part_2_prefix[part]:            
            if len(plist)>1:
                temp=temp.union(set(plist))
                if (debug==True):
                    print "plist: ",plist
    return dict.fromkeys(list(temp), '')

def getLCS(part_2_prefix):
    mds_out=[]
    for participant in part_2_prefix:
        plist=part_2_prefix[participant]
        for elem in plist:
            mds_out.append(frozenset(elem))
    mds_out=set(mds_out)
    mds=[]
    for elem in mds_out:
        mds.append(list(elem))    
    print 'mds_out: ',mds  
    return mds


def decompose_set(tdict,part_2_prefix_updated,tempdict_bk):
    #print "tdict: %s" % (tdict)
    pmap=[]
    for key in tdict:
        for lst in tdict[key]:
            pmap.append(set(lst))
    
    min_set=set.intersection(*pmap)
    if (debug==True):
        print pmap
        print "min_set: ",min_set
    if len(min_set)>0:
        for key in tdict:
            tlist=[min_set]
            for lst in tdict[key]:           
                temp=(set(lst).difference(min_set))   
                if len(temp)>0:
                    tlist.append(temp)
            tdict[key]=tlist
            part_2_prefix_updated[key]+=(tlist) 
            for elem in tempdict_bk[key]:
                part_2_prefix_updated[key].remove(elem)   
    return tdict

def decompose_simpler(part_2_prefix):
    part_2_prefix_updated=part_2_prefix
    pdict=get_pdict(part_2_prefix_updated)
    if (debug==True):
        print "pdict: ",pdict
    for key in pdict:
        #print key
        tempdict={}
        tempdict_bk={}
        for part in part_2_prefix_updated:
            #tempdict[part]=[]
            tlist=[]
            for temp in part_2_prefix_updated[part]:
                if key in temp:
                    tlist.append(temp)
            if len(tlist)>0:
                tempdict[part]=tlist
                tempdict_bk[part]=tlist
        if (debug==True):      
            print len(tempdict_bk),tempdict
        if (len(tempdict)==1 and len(tempdict.values()[0])==1) ==False:        
            decompose_set(tempdict,part_2_prefix_updated,tempdict_bk) 
        else:
            if (debug==True):
                print "Avoided"       
        if (debug==True):
            print part_2_prefix
    mds=[]
    for part in part_2_prefix_updated:
        for temp in part_2_prefix_updated[part]:
            tset=set(temp)
            if tset not in mds:
                mds.append(tset)
    if (debug==True):
        print "LCS: ",mds
    return part_2_prefix_updated,mds

def prefix_decompose(part_2_prefix):
    part_2_prefix_updated=part_2_prefix
    pdict=get_pdict(part_2_prefix_updated)
    for key in pdict:
        #print key
        tempdict={}
        for part in part_2_prefix_updated:
            #tempdict[part]=[]
            tlist=[]
            for temp in part_2_prefix_updated[part]:
                if key in temp:
                    tlist.append(temp)
            for elem in tlist:
                part_2_prefix_updated[part].remove(elem)
            if len(tlist)>0:
                tempdict[part]=tlist
        decomposed_tempdict=decompose_set(tempdict)
        for part in decomposed_tempdict:
            for elem in decomposed_tempdict[part]:
                part_2_prefix_updated[part].append(elem)
    return part_2_prefix_updated


def divide_part2prefixes(plist,part_2_prefix):
    tmp={}
    for elem in plist:
        tmp[elem]=part_2_prefix[elem]
    return tmp


def decmopose_parallel(part_2_prefix,q=None,index=0):
    part_2_prefix_updated={}
    partList=part_2_prefix.keys()
    P=len(partList)
    tmp1={}
    tmp2={}
    if (debug==True):
        print P
    if P==2:
        ndict={}
        keys=part_2_prefix.keys()
        nkey=str(keys[0])+str(keys[1]) 
        if (debug==True):
            print nkey       
        x,mds=decompose_simpler(part_2_prefix)
        if (debug==True):
            print part_2_prefix_updated
        ndict[nkey]=mds        
        return ndict  
    elif P==1:
        ndict={}
        if (debug==True):
            print part_2_prefix.keys()[0]
        x,mds=decompose_simpler(part_2_prefix)
        ndict[part_2_prefix.keys()[0]]=mds
        return ndict
    else:
        tmp1=divide_part2prefixes(partList[::2],part_2_prefix)
        tmp2=divide_part2prefixes(partList[1::2],part_2_prefix)
    
        #print tmp1,tmp2
        d1=decmopose_parallel(tmp1)
        d2=decmopose_parallel(tmp2)    
        mds=decmopose_parallel(dict(d1.items()+d2.items()))        
        return mds


def mds_parallel(part_2_prefix):
    mds=decmopose_parallel(part_2_prefix)     
    #print "Final LCS: ",mds
    part_2_prefix_updated={}
    # This step can be easily parallelized
    for part in part_2_prefix:
        d1={}
        d1[part]=part_2_prefix[part]

        p2p_tmp=dict(d1.items()+mds.items())
        if (debug==True):
            print "d1: ",d1
            print "mds: ",mds
            print "p2p: ",p2p_tmp
        tmp,x=decompose_simpler(p2p_tmp)
        part_2_prefix_updated[part]=tmp[part]
    if (debug==True):
        print "Final: ",part_2_prefix_updated
    return part_2_prefix,mds.values()[0]
    
   
def mds_recompute(p2p_old, p2p_new,part_2_prefix_updated,mds_old=[]):
    p2p_updated={}
    if len(mds_old)==0:
        mds_old=getLCS(part_2_prefix_updated)
    p2p_updated['old']=mds_old
    affected_participants=[]
    for participant in p2p_new:
        pset_new=get_pset(p2p_new[participant])
        pset_old=get_pset(p2p_old[participant])
        pset_new=(pset_new.union(pset_old).difference(pset_old))
        if len(pset_new)!=0:
            print "Re-computation required for: ",participant
            affected_participants.append(participant)
            plist=[]
            for elem in pset_new:
                plist.append(list(elem))
            p2p_updated[participant]=plist        
        print participant,pset_new
    print p2p_updated
    prefix_decompose(p2p_updated)
    for participant in part_2_prefix_updated:
        tmp={}
        if participant in affected_participants:
            tmp['new']=p2p_updated['old']
            tmp[participant]=part_2_prefix_updated[participant]
            prefix_decompose(tmp)
            p2p_updated[participant]=tmp[participant]
        else:
            p2p_updated[participant]=part_2_prefix_updated[participant]
    p2p_updated.pop('old')
    return p2p_updated


def decompose_simpler_multi(part_2_prefix,q=None):
    part_2_prefix_updated=part_2_prefix
    pdict=get_pdict(part_2_prefix_updated)
    print "pdict: ",pdict
    for key in pdict:
        print key
        tempdict={}
        tempdict_bk={}
        for part in part_2_prefix_updated:
            #tempdict[part]=[]
            tlist=[]
            for temp in part_2_prefix_updated[part]:
                if key in temp:
                    tlist.append(temp)
            if len(tlist)>0:
                tempdict[part]=tlist
                tempdict_bk[part]=tlist
        print len(tempdict_bk),tempdict
        if (len(tempdict)==1 and len(tempdict.values()[0])==1) ==False:        
            decompose_set(tempdict,part_2_prefix_updated,tempdict_bk)
        else:
            print "avoided" 
    mds=[]
    for part in part_2_prefix_updated:
        for temp in part_2_prefix_updated[part]:
            tset=set(temp)
            if tset not in mds:
                mds.append(tset)
    print "LCS: ",mds    
    if q!=None:
        q.put((part_2_prefix_updated,mds))
        print "Put operation completed", mp.current_process()
    else:
        return part_2_prefix_updated,mds
    
def decompose_multi(part_2_prefix,q=None,index=0):
    partList=part_2_prefix.keys()
    P=len(partList)
    print "Started, len: ",P,part_2_prefix.keys()
    if P==2:
        ndict={}
        keys=part_2_prefix.keys()
        nkey=str(keys[0])+str(keys[1])
        print nkey
        x,mds=decompose_simpler_multi(part_2_prefix)
        print part_2_prefix
        ndict[nkey]=mds
        print "Completed, len: ",P,part_2_prefix.keys()
        if q!=None: 
            q.put(ndict)
            print "Put operation completed", mp.current_process()
        else:      
            return ndict  
    elif P==1:
        
        ndict={}
        #print part_2_prefix.keys()[0]
        x,mds=decompose_simpler_multi(part_2_prefix)
        ndict[part_2_prefix.keys()[0]]=mds
        print "Completed, len: ",P,part_2_prefix.keys()
        if q!=None:
            q.put(ndict)
            print "Put operation completed", mp.current_process()
        else:
            return ndict
    else:
        tmp=[divide_part2prefixes(partList[::2],part_2_prefix),
             divide_part2prefixes(partList[1::2],part_2_prefix)]
        process=[]
        queue=[]
        qout=[]
        print tmp[0],tmp[1]
        for i in range(2):
            queue.append(Queue()) 
            process.append(Process(target=decompose_multi, args=(tmp[i],queue[i])))
            process[i].start()
            print "Started: ",process[i]
        for i in range(2):
            print "Waiting for: ",process[i],i
            qout.append(queue[i].get())
            process[i].join()
            print "Joined: ",process[i],i
              
        mds=decompose_multi(dict(qout[0].items()+qout[1].items()))  
        print "Completed, len: ",P,part_2_prefix.keys() 
        print mds 
        if q!=None:
            q.put(mds)
            print "Put operation completed", mp.current_process()
        else:    
            return mds

# Get the minimum number of Disjoint Sets given input sets    
def mds(part_2_prefix):
    mds=decompose_multi(part_2_prefix)     
    part_2_prefix_updated={}
    queue=[]
    process=[]
    i=0
    for part in part_2_prefix:
        d1={}
        d1[part]=part_2_prefix[part]
        print "d1: ",d1
        print "mds: ",mds
        tmp=dict(d1.items()+mds.items())
        print "tmp: ",tmp
        queue.append(Queue())
        process.append(Process(target=decompose_simpler_multi, args=(tmp,queue[i])))
        process[i].start()
        print "Started1: ",process[i]
        i+=1
    i=0
    for part in part_2_prefix:
        print "Waiting1 for: ",process[i],i
        tmp,x=queue[i].get()
        process[i].join()
        print "Joined1: ",process[i],i
        
        part_2_prefix_updated[part]=tmp[part]
        i+=1
    #print "Final LCS: ",mds
    #print "Final P2P: ",part_2_prefix_updated
    return part_2_prefix,mds.values()[0]




def main():
    part_2_prefix= {1: [[15, 2, 14, 13, 7, 4], [2, 12, 10, 14, 13, 11], [13, 7, 6, 1, 3, 12]], 
                    2: [[8, 13, 1, 11, 16, 10], [18, 16, 13, 17, 15, 7], [9, 14, 13, 2, 18, 17]],
                    3: [[17, 8, 5, 13, 1, 12], [6, 14, 1, 7, 13, 17], [14, 4, 9, 10, 16, 5]], 
                    4: [[11, 4, 18, 17, 5, 2], [9, 16, 8, 13, 7, 15], [3, 15, 6, 4, 5, 10]]}
    
    print part_2_prefix
    #mds=decompose_simpler(part_2_prefix)
    #part_2_prefix,mds=mds_parallel(part_2_prefix)
    part_2_prefix,mds=mds(part_2_prefix)
    print part_2_prefix

        

if __name__ == '__main__':
    main()  

    