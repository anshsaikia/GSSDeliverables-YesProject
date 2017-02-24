from BaseHTTPServer import BaseHTTPRequestHandler
import os
import json
import time
import calendar
import sys
import getopt
import datetime
import dateutil.parser

# ===========================================================
# GLOBAL CONFIGS
# ===========================================================

SERVER_ADDRESS     = "0.0.0.0"
SERVER_PORT        = 9000
TEST_SERVER		   = 0
dataFiles = "filesToServe/"

# ===========================================================
# RUN
# ===========================================================

class CTAPRequestType:
    REQUEST_UNKNOWN = 0
    REQUEST_CHANNELS = 1
    REQUEST_GRID = 2
    REQUEST_CONTENT_INSTANCE = 3

def getCTAPRequestType(path):
	print path
	try:
		pathComponents = path.split("?")
		pathComponents = pathComponents[0].split("/")
		if pathComponents[1].lower()!="ctap" or pathComponents[2]!="r1.0.0":
			return CTAPRequestType.REQUEST_UNKNOWN
		requestType = pathComponents[3]
		print requestType
		# http://10.57.36.69:8200/CTAP/1.5.0/agg/grid
		# http://10.57.36.69:8200/CTAP/1.5.0/channels
		# /CTAP/1.5.0/contentInstances/programid%3A%2F%2F10000~programid%3A%2F%2F30000
		if requestType == 'channels':
			print "channels request"
			return CTAPRequestType.REQUEST_CHANNELS
		elif requestType == 'agg' and pathComponents[4] == 'grid':
			print "grid request"
			return CTAPRequestType.REQUEST_GRID
		elif requestType == 'contentInstances':
			print "content instances request"
			return CTAPRequestType.REQUEST_CONTENT_INSTANCE
		else:
			print "unknown request!!"
			return CTAPRequestType.REQUEST_UNKNOWN
	except:
		return CTAPRequestType.REQUEST_UNKNOWN

def updateDatesInGrid(gridDict,now):
	services = gridDict["channels"]
	#try:
	for service in services:
		contents = service["schedule"]["events"]
		for content in contents:
			startTime = content["startTime"]
			#print startTime
			epochTime = dateutil.parser.parse(startTime)
			epochTime = epochTime + datetime.timedelta(seconds=now)
			isoString = epochTime.isoformat()
			plusIndex = isoString.index("+")
			if plusIndex != -1:
				isoString = isoString[:plusIndex]
			content["startTime"] = isoString +".000Z"
	#except Exception, err:
	#	print Exception, err
	return gridDict

def updateDatesInContentInstance(contentInstanceDict,now):
	try:
		startTime = contentInstanceDict["startTime"]
		epochTime = dateutil.parser.parse(startTime)
		epochTime = epochTime + datetime.timedelta(seconds=now)
		isoString = epochTime.isoformat()
		plusIndex = isoString.index("+")
		if plusIndex != -1:
			isoString = isoString[:plusIndex]
		contentInstanceDict["startTime"] = isoString +".000Z"
	except Exception, err:
		print Exception, err
	return contentInstanceDict

def getResponse(path):
	now = calendar.timegm(time.gmtime())
	requestType = getCTAPRequestType(path)
	if requestType == CTAPRequestType.REQUEST_UNKNOWN:
		return {"data": "Not Found", "statusCode":404}
	fileToLoad = None
	data = None
	pathToFile=dataFiles
	#try to find exact file, if fails, use the generic one
	pathComponents = path.split("/")
	indexOfStart=pathComponents[-1].find("startDateTime")
	if indexOfStart!=-1:
		indexEnd=pathComponents[-1][indexOfStart:].index("&")
		normalizedStr = pathComponents[-1][0:indexOfStart]+"startDateTime=0"+pathComponents[-1][indexOfStart+indexEnd:]
		pathComponents[-1] = normalizedStr
	if "~" in pathComponents[-1]:
		pathComponents[-1] = pathComponents[-1].replace("~", "%7E")
	postFixUrl = "#".join(pathComponents[3:])
	if postFixUrl.endswith("#"):
		postFixUrl = postFixUrl[0:-1]
	postFixUrl = postFixUrl.replace("?","#")
	#why do I need this? something weird
	postFixUrl = postFixUrl.replace("##","#")
	fileNameToLookFor = pathToFile+postFixUrl+".json"
	print fileNameToLookFor
	if os.path.exists(fileNameToLookFor):
		fileToLoad = fileNameToLookFor
	#in this mode, don't parse exact responses, just return the generic one
	if TEST_SERVER==1:
		fileToLoad=None
	if not fileToLoad:
		if requestType == CTAPRequestType.REQUEST_CHANNELS:
			fileToLoad = pathToFile+"channelsResponse.json"
		elif requestType == CTAPRequestType.REQUEST_GRID:
			fileToLoad = pathToFile+"gridResponse.json"
		elif requestType == CTAPRequestType.REQUEST_CONTENT_INSTANCE:
			fileToLoad = pathToFile+"contentInstancesResponse.json"
	print "serving " + fileToLoad
	if fileToLoad:
		with open(fileToLoad) as data_file:
			data = data_file.read()
			if requestType == CTAPRequestType.REQUEST_GRID:
				origData = json.loads(data)
				updatedData = updateDatesInGrid(origData, now)
				data = json.dumps(updatedData)
			elif requestType == CTAPRequestType.REQUEST_CONTENT_INSTANCE:
				origData = json.loads(data)
				updatedData = updateDatesInContentInstance(origData,now)
				data = json.dumps(updatedData)
	if data:
			return {"data":data, "statusCode":200}
	print "unknown request : " + path
	return {"data": "Not Found", "statusCode":404}


class GetHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		response = getResponse(self.path)
		#print response
		self.send_response(response["statusCode"])
		self.send_header("Content-type", "application/json")
		self.end_headers()
		self.wfile.write(response["data"])


if __name__ == '__main__':
	from BaseHTTPServer import HTTPServer
	try:
		opts, args = getopt.getopt(sys.argv[1:],"hm:d:",["m=","d="])
	except getopt.GetoptError:
		print 'python server.py -m <runmode> -d <dataToServe>'
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print 'python server.py -m <runmode> -d <dataToServe>'
			sys.exit()
		elif opt in ("-m", "--m"):
			mode = arg
			if mode == "test":
				TEST_SERVER=1
			else:
				TEST_SERVER=0
		elif opt in ("-d", "--d"):
			dataFiles = arg
			if not dataFiles.endswith("/"):
				dataFiles = dataFiles+"/"
	server = HTTPServer((SERVER_ADDRESS, SERVER_PORT), GetHandler)
	print "Starting server on port " + str(SERVER_PORT) + ", use <Ctrl-C> to stop"
	server.serve_forever()
