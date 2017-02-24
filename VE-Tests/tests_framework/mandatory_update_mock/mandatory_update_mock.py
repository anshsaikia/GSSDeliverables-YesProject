#http://wikicentral.cisco.com/display/VIDEOSCAPE/VE+Requiring+SW+Application+Upgrade+on+Devices
import threading
import web
import httplib
import sys
import socket
import json


"Constants"
DEFAULT_VERSION = "1.1"

def getLocalIP():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("gmail.com", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


class MandatoryUpdateSimulator(object):
    def __init__(self):
        self.web_server = web.application(('/.*', 'RequestsHandler'), globals())
        MandatoryUpdateSimulator.ip = getLocalIP()

    def start(self):
        sys.argv[1:] = [MandatoryUpdateSimulator.ip]
        self.server_thread = threading.Thread(target=self.web_server.run)
        self.server_thread.daemon = True
        self.server_thread.start()

    def stop(self):
        self.web_server.stop()


class RequestsHandler(object):
    def __init__(self):
        self.response_status = httplib.OK


    def minAllowedVersion(self):
        if hasattr(RequestsHandler, 'version'):
            minimum_version = RequestsHandler.version
        else:
            minimum_version = DEFAULT_VERSION
        response = {}
        response['MinAllowedVersion'] = minimum_version
        min_version = json.dumps(response)
        return min_version


    def set_min_version(self, version):
        RequestsHandler.version = version

    def set_response_status(self, status):
        self.response_status = status

    def GET(self):
        res = self.minAllowedVersion()
        return res

    def POST(self):
        updated_version = web.input().minAllowedVersion
        self.set_min_version(updated_version)
        return

if __name__ == "__main__":
    sys.argv.append("5055")
    server = MandatoryUpdateSimulator()
    server.start()
    # import time
    # time.sleep(40)
    # server.stop()

