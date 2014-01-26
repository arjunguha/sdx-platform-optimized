import os,json,sys
recursionLimit=100000

def main(option):
    cmd='python evalCollector.py '+option+' &'
    os.system(cmd)
    

if __name__ == '__main__':
    sys.setrecursionlimit(recursionLimit)
    main(sys.argv[1])