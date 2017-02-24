__author__ = 'isinitsi'

import threading
import socket
import os.path
from BaseHTTPServer import HTTPServer
from BaseHTTPServer import BaseHTTPRequestHandler
from random import randint


HTTP_HOME = "KD/android/DummyData/dummy_data"


def getLocalIP():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("gmail.com", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip

class GetHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        if len(self.path) > 0:
            if not os.path.isfile(HTTP_HOME + self.path):
                self.send_error(404, "File not found")
                return
        else:
            self.send_error(404, "No file requested")
            return

        file = open(HTTP_HOME + self.path)

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(file.read())
        file.close()
        return

class SimpleHttpServer():


    def __init__(self):
        ip = getLocalIP()
        port = 7500

    def try_to_start_server(self):
        self.port = randint(5000, 9000)
        self.server = HTTPServer((self.ip, self.port), GetHandler)
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()

    def start(self):
        for index in range(0,2):
            try:
                self.try_to_start_server()
                break
            except Exception as inst:
                print inst.args
                print inst.message
                assert index != 3

    def waitForThread(self):
        self.server_thread.join()

    def stop(self):
        self.server.shutdown()
        self.waitForThread()



# def startHTTPServer():
#
#     PORT = 7500
#     server = HTTPServer(('0.0.0.0', PORT), GetHandler)
#     server.serve_forever()



