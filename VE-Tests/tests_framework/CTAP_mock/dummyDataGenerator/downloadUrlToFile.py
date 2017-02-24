import urllib2
import os
import sys
import json
import time
import calendar

jsonDir = "generated/"
		
def download(url, filePath):
	#download from url
	print "downloading from " + url
	grid = urllib2.urlopen(url)
	localServiceFile=open(filePath,"w+")
	localServiceFile.write(grid.read())
	localServiceFile.close()
	return filePath
	
def normalize(gridDict, downloadDate):
	services = gridDict["channels"]
	try:
		for service in services:
			contents = service["schedule"]["events"]
			for content in contents:
				#print content
				if "startTime" in content:
					startTime = content["startTime"]
					content["startTime"] = startTime - downloadDate*1000
				if ("endAvailability" in content):
					content["endAvailability"] = endTime - downloadDate*1000
				print content
	except Exception, err:
		print Exception, err

def main(args):
	if (len(args)<3):
		print "no url or file name given! \nusage: downloadUrlToFile.py <urlToDownloadFrom> <fileNameToSaveInfoIn>"
		sys.exit(1)
	url = args[1]
	if not os.path.exists(jsonDir):
		os.makedirs(jsonDir)
	fileName = jsonDir+args[2]
	downloadDate = calendar.timegm(time.gmtime())
	download(url, fileName)
	with open(fileName, "r+") as data_file:    
		contentsDict = json.load(data_file)
		normalize(contentsDict, downloadDate)
		data_file.seek(0)
		json.dump(contentsDict, data_file)
	
main(sys.argv)