import os
import web
import json
import threading
import sys
import httplib
import socket


urls = (
  "/(.*)", "index"
)

script_dir = os.path.dirname(__file__)
file_path = os.path.join(script_dir, 'error_response.json')
error_response_data = json.loads(open(file_path).read())

class responseServer(object):
    def __init__(self):
        self.web_server = web.application(('/(.*)', 'index'), globals())
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("gmail.com", 80))
        ip = s.getsockname()[0]
        s.close()
        print "web application server in error verification is:",ip
        responseServer.ip = ip


    def start(self):
        sys.argv[1:] = [responseServer.ip]
        self.server_thread = threading.Thread(target=self.web_server.run)
        self.server_thread.daemon = True
        self.server_thread.start()

    def stop(self):
        self.web_server.stop()


class index:
    def __init__(self):
        self.response_status = httplib.OK

    def getErrorContext(self,tmp):
        result = []
        result = tmp.split('/')
        return result[0]

    def getErrorResponse(self,context_id):
        web.header('Content-Type', 'application/json')
        responseData = error_response_data[context_id]
        web.ctx.status = responseData["httpErrorCode"]
        return json.dumps(responseData["response"])


    def GET(self,name):
        context_id = self.getErrorContext(name)
        return self.getErrorResponse(context_id)

    def POST(self,name):
        context_id = self.getErrorContext(name)
        return self.getErrorResponse(context_id)


if __name__ == "__main__":
    #app = web.application(urls, globals())
    #app.run()
    #sys.argv.append("5555")
    server = responseServer()
    server.start()