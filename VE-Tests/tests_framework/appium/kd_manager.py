
import os
import socket
import thread
import subprocess
import signal
from threading import Lock
from time import sleep

''' Global Constants '''
CLIENT_RESPONSE = None
TIME_OUT = 35
FIRST_LAUNCH_TIMEOUT = 20
DEPLOY_TIMEOUT = 60

class KDManager:
    def __init__(self, test):
        self.test = test
        self.server = None

    def store_ip(self, device_ip):
        self.test.log_assert(device_ip, "Cannot receive ip from device")
        current_device_ip = self.test.device_ip
        if current_device_ip:
            current_device_port = current_device_ip.split(':')[1]
        else:
            current_device_port = self.test.device_port

        self.test.log_assert(device_ip != "0.0.0.0", "Device ip is " + device_ip + " !!!, Please check device WiFi.")
        self.test.device_ip = device_ip + ":" + current_device_port
        self.test.log("Found ip for device: " + self.test.device_ip)

    def parse_param(self, string, param):
        searchToken = param + "=\""
        startIndex = string.find(searchToken)
        self.test.log_assert(startIndex != -1, "Cannot find param '" + param + "' in response: " + str(string))
        paramString = string[startIndex+len(searchToken):]
        endIndex = paramString.find("\"")
        self.test.log_assert(endIndex != -1, "Cannot find end quote for '" + param + "' in param string: " + str(paramString))
        ip = paramString[:endIndex]
        self.test.log_assert(ip, "Cannot find parameter for '" + param + "' in param string: " + str(paramString))
        return ip

    def launch(self, launchApp=True):
        app = None
        if self.test.manage_app:
            self.test.app_launched = False
            if self.test.install_manage:
                result = False
                self.test.wait(1)
                os.system('pwd')

                deviceId = self.test.device_id
                self.test.log("deviceId: " + deviceId)

                cmd = "xcodebuild test -workspace ./../ec_utils/ios/KDManager/KDManager.xcworkspace/ -scheme KDManager -derivedDataPath ./build -destination 'platform=iOS,id=" + deviceId + "' GCC_PREPROCESSOR_DEFINITIONS='"
                if launchApp:
                    cmd += "PRODUCT=\\\"" + self.test.project + "\\\""
                if self.test.dynamicIp:
                    cmd += " RETURN_IP "
                cmd += "'"
                if self.test.verbose:
                    cmd += " -verbose"
                cmd += " | tee output"
                self.test.log("calling: " + cmd)
                try:
                    response = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
                except Exception as e:
                        self.test.log_assert(False, "Failed to compile and launch KDManager, error=%s" % e)
                if self.test.dynamicIp:
                    ip = self.parse_param(response, "ip")
                    self.store_ip(ip)
            elif launchApp:
                self.test.milestones.launch()

            if launchApp:
                self.test.stop_app = True
