import os,sys,random

add_cache={}

class Inside():
    def __init__(self,v):
        
        self.v=v
        print self.v

class Test():
    def __init__(self,a=1):
        self.a=a
    def local_test(self):
        for j in range(3):
            k=random.randint(1,100)
            if k not in add_cache:
                v=Inside(random.randint(1,100))
                add_cache[k]=v
                print "Added k: ",k," v: ",v

def main():
    print "main called"
    for i in range(5):

        testobj=Test()
        testobj.local_test()
    print map(lambda x: type(x),add_cache.values())
    
    
if __name__ == '__main__':
    main()