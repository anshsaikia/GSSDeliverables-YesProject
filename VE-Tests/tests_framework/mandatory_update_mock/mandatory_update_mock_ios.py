#http://wikicentral.cisco.com/display/VIDEOSCAPE/VE+Requiring+SW+Application+Upgrade+on+Devices
from BaseHTTPServer import BaseHTTPRequestHandler
from BaseHTTPServer import HTTPServer
from SocketServer import ThreadingMixIn
import json
import subprocess
import threading
import time

"Constants"
DEFAULT_VERSION = "1"
SERVER_ADDRESS     = "0.0.0.0"
SERVER_PORT        = 8076

global Version
Version = None
global stop_event
stop_event = threading.Event()

class GetHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if Version:
            minimum_version = Version
        else:
            minimum_version = DEFAULT_VERSION
        response = {"MinAllowedVersion":minimum_version}
        print response
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response))

    def set_min_version(self, versionToSet):
        global Version
        print "setting version to " + versionToSet
        Version = versionToSet

    def do_POST(self):
        content_len = int(self.headers.getheader('content-length', 0))
        post_body = self.rfile.read(content_len)
        self.set_min_version(post_body)
        self.send_response(200)


class ThreadedHttpServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread. Taken from: https://pymotw.com/2/BaseHTTPServer/index.html#module-BaseHTTPServer"""

class MandatoryUpdateSimulator(ThreadingMixIn,HTTPServer):
    def __init__(self):
        machineIp = subprocess.check_output("ifconfig en0 | grep inet | grep -v inet6 | awk '{print $2}'", shell=True)
        if machineIp.endswith("\n"):
            machineIp = machineIp[0:-1]
        MandatoryUpdateSimulator.ip = machineIp+":8076"
        MandatoryUpdateSimulator.server = None

    def start(self):
        try:
            subprocess.call("lsof -n -i:8076 | grep LISTEN | awk '{ print $2 }' | uniq | xargs kill -9")
            print "after kill"
        except Exception, e:
            print "problem in stopping threads: " + str(e)
            pass
        try:
            MandatoryUpdateSimulator.server = ThreadedHttpServer((SERVER_ADDRESS, SERVER_PORT), GetHandler)
        except Exception, e:
            print "server could not be started: " + str(e)
            return
        print "Starting server on " + MandatoryUpdateSimulator.ip + ", use <Ctrl-C> to stop"
        MandatoryUpdateSimulator.server.serve_forever()

    def stop(self):
        self.stop.set()

if __name__ == "__main__":
    server = MandatoryUpdateSimulator()
    print "1"
    serving = threading.Thread(target=server.start)
    stop_server = threading.Event()
    print "2"
    serving.start()
    time.sleep(10)
    print "3"
    server.stop()
    print "4"

