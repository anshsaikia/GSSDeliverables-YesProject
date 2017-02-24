
import sys, thread, socket, web
from threading import Lock
from commands import getstatusoutput
from time import sleep
from json import loads

''' Global Constants '''
MINIMUM_FREE_DEVICE_STORAGE = 100
CLIENT_RESPONSE = None
TRIES = 2
TIME_OUT = 10


class ServerHandler():
    def POST(self):
        global CLIENT_RESPONSE
        response = loads(web.data())
        CLIENT_RESPONSE = response     
        return "OK"


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("www.google.com", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


def usage(reason):
    if reason: print reason
    print "Usage: android_health_check.py <device_id> <response_port>"
    assert 0


def check_arguments():
    if len(sys.argv) != 3:
        usage("Wrong arguments")
        
    devices = []
    for i in getstatusoutput("adb devices | grep -v List | cut -f 1")[1].split(): 
        if i != "": devices.append(i)
         
    if not sys.argv[1] in devices:
        usage("Wrong arguments")


def is_device_on(device_id):
    status = getstatusoutput("adb -s " + device_id + " shell dumpsys power | grep mWakefulness=")[1].split("=")[1]
    return status.replace("\r", "").replace("\n", "") == "Awake"


def trigger_device():
    global CLIENT_RESPONSE
    
    getstatusoutput('adb -s ' + deviceId + ' shell am broadcast -a "HEALTH_CHECK" -n com.cisco.healthcheckapp/.HealthCheckRequestsHandler --es "DEVICE_ID" ' + deviceId + ' --es "RESPONSE_IP" ' + get_local_ip() + ':' + port)
    lock = Lock()
    for i in range(TIME_OUT):
        lock.acquire()
        if CLIENT_RESPONSE is not None and CLIENT_RESPONSE["device_id"] == deviceId:
            break
        lock.release()
        sleep(1)

if __name__ == "__main__":
    check_arguments()
    deviceId = sys.argv[1]
    port = sys.argv[2]
    sys.argv[1] = port 
    
    urls = ('/.*', 'ServerHandler')
    app = web.application(urls, globals())  
    thread.start_new_thread(app.run, ())
    
    if not is_device_on(deviceId):
        getstatusoutput("adb -s " + deviceId + " shell input keyevent 26")
        
    for i in range(TRIES):
        trigger_device()
        if CLIENT_RESPONSE is not None:
            break
        
    assert CLIENT_RESPONSE
    assert int(CLIENT_RESPONSE["disk_space"]) > MINIMUM_FREE_DEVICE_STORAGE
    assert not CLIENT_RESPONSE["ip"] == "null"
    assert not CLIENT_RESPONSE["network"] == "blizzard"
    
    print "\n\n"
    for key in CLIENT_RESPONSE:
        getstatusoutput('ectool setProperty "/myParent/'+str(key).upper()+'" --value "'+str(CLIENT_RESPONSE[key])+'"')
        print str(key) + ": " + str(CLIENT_RESPONSE[key])
    print "\n\n"