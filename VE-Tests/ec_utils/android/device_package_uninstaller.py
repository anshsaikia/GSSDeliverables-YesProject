

import sys
from commands import getstatusoutput

def usage(reason):
    if(reason): print reason
    print "Usage: android_package_uninstaller.py <device_id> <package name>"
    assert 0
        
def checkArguments():
    if(len(sys.argv) != 3):
        usage("Wrong arguments")
        
    devices = []
    for i in getstatusoutput("adb devices | grep -v List | cut -f 1")[1].split(): 
        if(i != ""): devices.append(i)
         
    if(not sys.argv[1] in devices): 
        usage("Wrong arguments")
        
def uninstall(deviceId, package):
    res = getstatusoutput("adb -s " + deviceId + " uninstall " + package)[1]
    assert "Success" in res
    
    
checkArguments()
uninstall(sys.argv[1], sys.argv[2])
        