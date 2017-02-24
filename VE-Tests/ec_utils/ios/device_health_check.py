import os
import sys
import thread
import socket
import web
from threading import Lock
from commands import getstatusoutput
from time import sleep
from json import loads

''' Global Constants '''
CLIENT_RESPONSE = None
TIME_OUT = 35
KD_ROOT_PATH = "~/Public/VE-Tests"
KD_MANAGER_APP_PATH = "/tests/KD/KDManager.app"
KD_MANAGER_CODE_PATH = "/ec_utils/ios/KDManager/KDManager.xcworkspace/"
VERBOSE= True

class ServerHandler(object):
    def __init__(self):
        pass

    def POST(self):
        global CLIENT_RESPONSE
        CLIENT_RESPONSE = loads(web.data())
        return "OK"

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("www.google.com", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


def usage(reason=None):
    if reason:
        print reason
    print "Usage: device_health_check.py <udid> <response_port>"
    assert 0


def check_arguments():
    if len(sys.argv) < 3:
        usage("Wrong arguments")

    print "Plugged devices:", getstatusoutput("ios-deploy -c")
    for line in getstatusoutput("ios-deploy -c")[1].split():
        if sys.argv[1] in line:
            return
    usage("Wrong arguments (Please check if device ID that came from ios deploy is same for device ID that was defined in CI cloud resource")

def trigger_device_alt(udid):
    global CLIENT_RESPONSE
    cmd = "xcodebuild test -workspace " + KD_ROOT_PATH + KD_MANAGER_CODE_PATH + " -scheme KDManager -destination 'platform=iOS,id=" + udid + "' GCC_PREPROCESSOR_DEFINITIONS='EC_MACHINE_IP=\\\"http://" + get_local_ip()+":" + port + "\\\"'"
    if not VERBOSE:
        cmd += " | egrep -A 5 \"(error|warning):\""
    print "calling: " + cmd
    os.system(cmd)
    lock = Lock()
    for i in range(TIME_OUT):
        lock.acquire()
        if CLIENT_RESPONSE is not None:
            break
        lock.release()
        sleep(1)
    sleep(5)

def trigger_device(udid):
    global CLIENT_RESPONSE
    # commented due to killing when 2 devices are connected to same computer. terminate with reason 15
    # os.system("pkill ios-deploy")
    # os.system("pkill lldb")
    print "ios-deploy --id " + udid + " --justlaunch  --noninteractive --bundle " + KD_ROOT_PATH + KD_MANAGER_APP_PATH + " --args ec_machine_ip=http://" + get_local_ip()+":" + port
    print getstatusoutput("ios-deploy --id " + udid + " --justlaunch  --noninteractive --bundle " + KD_ROOT_PATH + KD_MANAGER_APP_PATH + " --args ec_machine_ip=http://" + get_local_ip()+":"+port)
    lock = Lock()
    for i in range(TIME_OUT):
        lock.acquire()
        if CLIENT_RESPONSE is not None:
            break
        lock.release()
        sleep(1)

if __name__ == "__main__":
    print "Input Arguments:", sys.argv
    check_arguments()
    udid = sys.argv[1]
    port = sys.argv[2]
    sys.argv[1] = port

    if len(sys.argv) > 3:
        KD_ROOT_PATH = sys.argv[3]
    
    urls = ('/.*', 'ServerHandler')
    app = web.application(urls, globals())  
    thread.start_new_thread(app.run, ())
    trigger_device_alt(udid)
        
    assert CLIENT_RESPONSE
    assert CLIENT_RESPONSE["device_ip"]
    print "\n\nHealth check test received the following ip:", CLIENT_RESPONSE["device_ip"], "for UDID:", udid, "\n\n"

    shared_file = open("device_ip.txt", "w")
    shared_file.write(CLIENT_RESPONSE["device_ip"])
    shared_file.close()
