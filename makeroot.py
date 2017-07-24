#! /home/creamop/miniconda3/bin/python
import os

def makeroot(files):
    makeroot_dir = '/home/creamop/L0data'
    os.chdir(makeroot_dir)
#    os.system('./list_override')
#    os.chdir('cream/')
#    f = open('LIST','w')
#    for i in range(0,len(files)):
#        f.write(files[i])
#    f.close()
#    os.chdir(L0_directory)
    os.system('./makeroot_trigger_rate')
