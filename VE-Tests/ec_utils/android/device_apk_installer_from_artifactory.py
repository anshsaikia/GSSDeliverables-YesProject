
import sys, os
from commands import getstatusoutput

def usage(reason):
    if(reason): print reason
    print "Usage: android_apk_installer.py <device_id> <apk_path>"
    assert 0
    
def checkArguments():
    
    if(len(sys.argv) != 4):
        usage("Wrong arguments")
        
    if(not os.path.isfile(sys.argv[2]) or not sys.argv[2].endswith(".apk")):
        usage("Wrong apk: " + sys.argv[2])
        
    devices = []
    for i in getstatusoutput("adb devices | grep -v List | cut -f 1")[1].split(): 
        if(i != ""): devices.append(i)
         
    if(not sys.argv[1] in devices): 
        usage("Wrong device id")
        

def install(deviceId, apkName, apkPath):
    res = getstatusoutput("adb -s " + deviceId + " install -r " + apkPath + "/" + apkName)[1]
    print res
    assert "Success" in res
  
checkArguments()
install(sys.argv[1], sys.argv[2], sys.argv[3])
