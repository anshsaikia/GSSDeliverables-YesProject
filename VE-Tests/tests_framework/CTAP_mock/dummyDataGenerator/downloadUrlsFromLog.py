import sys
import shutil
import urllib2
import os
import json
import time
import calendar
import urllib
import datetime
import dateutil.parser

jsonDir = "generated"
ctapHeaders = {'x-cisco-vcs-identity' : '{"hhId":"h6", "upId":"h6_0", "sessionId":"6e498d70-7ba2-11e4-957e-bd9ae1622e27", "devId":"123", "cmdcRegion": "16384~16385","region": "1","tenant":"kd",""deviceFeatures": ["COMPANION", "ABR"],"cmdcDeviceType": "COMPANION"}'}
		
def download(url, filePath):
	#download from url
	request = urllib2.Request(url, headers = ctapHeaders)
	grid = urllib2.urlopen(request)
	localServiceFile=open(filePath,"w+")
	localServiceFile.seek(0)
	localServiceFile.write(grid.read())
	localServiceFile.truncate()
	localServiceFile.close()
	return filePath
	
def normalize(gridDict, downloadDate):
	services = gridDict["channels"]
	try:
		for service in services:
			contents = service["schedule"]["events"]
			for content in contents:
				startTime = content["startTime"]
				epochTime = dateutil.parser.parse(startTime)
				epochTime = epochTime - datetime.timedelta(seconds=downloadDate)
				isoString = epochTime.isoformat()
				plusIndex = isoString.index("+")
				if plusIndex != -1:
					isoString = isoString[:plusIndex]
				content["startTime"] = isoString +".000Z"
	except Exception, err:
		print Exception, err

def normalizeInstance(content, downloadDate):
	#try:
	startTime = content["startTime"]
	#2015-07-22T15:00:00.000Z
	epochTime = dateutil.parser.parse(startTime)
	epochTime = epochTime - datetime.timedelta(seconds=downloadDate)
	isoString = epochTime.isoformat()
	plusIndex = isoString.index("+")
	if plusIndex != -1:
		isoString = isoString[:plusIndex]
	content["startTime"] = isoString +".000Z"
	#except Exception, err:
	#	print Exception, err
	
def createUrlSet(fileName):
	urlSet=set()
	with open(fileName) as data_file:
		for line in data_file:
			if "CTAP/r1.0.0" in line:
				startIndex = line.find("http://")
				line = line[startIndex:]
				endIndex = line.find(" ")
				if endIndex == -1:
					endIndex = line.find("/n");
				url = line[:endIndex]
				urlSet.add(url)
	return urlSet	

def downloadContentInstance(url, gridDict, downloadDate):
	CTAPindex = url.index("CTAP/r1.0.0")
	ctapUrl = url[:CTAPindex]
	print ctapUrl
	services = gridDict["channels"]
	for service in services:
		try:
			contents = service["schedule"]["events"]
			for content in contents:
				print content["id"]
				contentInstanceUrl = ctapUrl+"CTAP/r1.0.0/contentInstances/"+urllib.quote(content["id"],safe='')
				print contentInstanceUrl
				pathComponents = contentInstanceUrl.split("?")
				pathComponents = pathComponents[0].split("/")+pathComponents[1:]
				postFixUrl = "#".join(pathComponents[5:])
				responseFileName = jsonDir+"/"+postFixUrl+".json"
				if os.path.exists(responseFileName):
					print "not downloading " + contentInstanceUrl +", file already exists"
					continue
				print "downloading "+ contentInstanceUrl+" into : " + responseFileName
				download(contentInstanceUrl, responseFileName)
				with open(responseFileName, "r+") as data_file:    
					#normalize the entries and download the content instance for each instance
					contentsDict = json.load(data_file)
					normalizeInstance(contentsDict, downloadDate)
					data_file.seek(0)
					json.dump(contentsDict, data_file)
					data_file.truncate()
		except Exception, err:
			print Exception, err
				
def main(args):
	if (len(args)<2):
		print "no log file given!"
		sys.exit(1)
	logFile = args[1]
	if not os.path.exists(logFile):
		print "couldn't find file"
		sys.exit(1)
	if os.path.exists(jsonDir):
		shutil.rmtree(jsonDir)
	if not os.path.exists(jsonDir):
		os.makedirs(jsonDir)
	urlSet = createUrlSet(logFile)
	for url in urlSet:
		#get url parts
		pathComponents = url.split("?")
		pathComponents = pathComponents[0].split("/")+pathComponents[1:]
		indexOfStart=pathComponents[-1].find("startDateTime")
		if indexOfStart!=-1:
			indexEnd=pathComponents[-1][indexOfStart:].index("&")
			normalizedStr = pathComponents[-1][0:indexOfStart]+"startDateTime=0"+pathComponents[-1][indexOfStart+indexEnd:]
			pathComponents[-1] = normalizedStr
		postFixUrl = "#".join(pathComponents[5:])
		responseFileName = jsonDir+"/"+postFixUrl+".json"
		if os.path.exists(responseFileName):
			print "not downloading " + url +", file already exists"
			continue
		print "downloading "+url+" into : " + responseFileName
		downloadDate = calendar.timegm(time.gmtime())
		download(url, responseFileName)
		if "grid" in pathComponents:
			with open(responseFileName, "r+") as data_file:    
				#normalize the entries and download the content instance for each instance
				contentsDict = json.load(data_file)
				downloadContentInstance(url, contentsDict, downloadDate)
				normalize(contentsDict, downloadDate)
				data_file.seek(0)
				json.dump(contentsDict, data_file)
				data_file.truncate()
		elif "contentInstance" in pathComponents:
			with open(responseFileName, "r+") as data_file:    
				#normalize the entries and download the content instance for each instance
				contentsDict = json.load(data_file)
				normalizeInstance(contentsDict, downloadDate)
				data_file.seek(0)
				json.dump(contentsDict, data_file)
				data_file.truncate()


main(sys.argv)