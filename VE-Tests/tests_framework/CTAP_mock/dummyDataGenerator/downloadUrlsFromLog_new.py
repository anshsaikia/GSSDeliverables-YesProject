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

#jsonDir = "/Users/abarilan/iOS_KD/ytv-kd-ios-app/WhitelabelApps/ProductKD/Resources/Preloaded"
jsonDir="Preloaded"
imagesDir = "/cachedImagesThumbnails/"
ctapHeaders = {'x-cisco-vcs-identity' : '{"cmdcDeviceType":"IOS","upId":"h6_0","sessionId":"7fb21d5d-6ff4-4940-86df-6aaedc0c57bb","cmdcRegion":"16384~16385","hhId":"h6_HH","devId":"123","deviceFeatures":["COMPANION","ABR","WIFI-CHIP"],"tenant":"kd","region":"100"}','X-Forwarded-For': "10.149.204.104"}		
downloadedImages=[]
downloadedPosters=[]
downloadedLogos=[]
imagesIndex=0
logosIndex=0
postersIndex=0

def download(url, filePath):
	print url
	if os.path.exists(filePath):
		print "not downloading: "+ filePath+" already exists"
		return None
	#download from url
	try:
		request = urllib2.Request(url, headers = ctapHeaders)
		grid = urllib2.urlopen(request)
		localServiceFile=open(filePath,"w+")
		localServiceFile.seek(0)
		localServiceFile.write(grid.read())
		localServiceFile.truncate()
		localServiceFile.close()
		return filePath
	except Exception, err:
		print "download"
		print Exception, err
		return None

def handleMedia(content, logo=False, poster=False):
	global imagesIndex
	global logosIndex
	global postersIndex
	global downloadedImages
	global downloadedLogos
	global downloadedPosters
	inside=False
	if "media" in content:
		media = content["media"]
	elif "content" in content and "media" in content["content"]:
		media = content["content"]["media"]
		inside=True
	#download first image and delete everything else
	medIndex=0
	while len(media)>medIndex:
		uri = media[medIndex]["uri"]
		if not uri.endswith(".png") and not uri.endswith(".jpg"):
			medIndex=medIndex+1
		else:
			if poster:
				#try to find poster
				if media[medIndex]["height"]<media[medIndex]["width"] and len(media)>medIndex+1:
					medIndex=medIndex+1
				else:
					break
			else:
				break
	if len(media)>medIndex:
		if logo:
			print "logo"
			downloadTo=downloadedImages
			downloadLimit=20
			index=imagesIndex
		elif poster:
			print "poster"
			downloadTo=downloadedPosters
			downloadLimit=20
			index=postersIndex
		else:
			print "landscape"
			downloadTo=downloadedLogos
			downloadLimit=20
			index=logosIndex
		if len(downloadTo)<downloadLimit:
			#fileName=media[medIndex]["uri"].replace("/","_").replace(":","_")+".img"
			fileName = media[medIndex]["uri"].split("/")[-1]
			returnedPath = download(media[medIndex]["uri"],jsonDir+imagesDir+fileName)
			if inside:
				content["content"]["media"]=[media[medIndex]]
			else:
				content["media"]=[media[medIndex]]
			if returnedPath:
				downloadTo.append(media[medIndex])
			print "generated media - downloaded"
		else:
			if inside:
				content["content"]["media"] = [downloadTo[index]]
			else:
				content["media"] = [downloadTo[index]]
			if logo:
				logosIndex=(index+1)%downloadLimit
			elif poster:
				postersIndex=(index+1)%downloadLimit
			else:
				imagesIndex=(index+1)%downloadLimit
			print "generated media - already downloaded"
		if inside:
			print content["content"]["media"]
		else:
			print content["media"]

def normalizeGrid(gridDict, downloadDate):
	#print "normalizeGrid"
	services = gridDict["channels"]
	try:
		for service in services:
			if "schedule" in service:
				contents = service["schedule"]#["events"]
				for content in contents:
					#start time
					startTime = content["startDateTime"]
					epochTime = dateutil.parser.parse(startTime)
					epochTime = epochTime - datetime.timedelta(seconds=downloadDate)
					isoString = epochTime.isoformat()
					plusIndex = isoString.index("+")
					if plusIndex != -1:
						isoString = isoString[:plusIndex]
					content["startDateTime"] = isoString +".000Z"
					#media
					handleMedia(content)
			handleMedia(service, True)
	except Exception, err:
		print "normalize"
		print service
		print Exception, err
		exit(1)

def normalizeInstance(content, downloadDate):
	#try:
	if "startDateTime" in content:
		startTime = content["startDateTime"]
		#2015-07-22T15:00:00.000Z
		epochTime = dateutil.parser.parse(startTime)
		epochTime = epochTime - datetime.timedelta(seconds=downloadDate)
		isoString = epochTime.isoformat()
		plusIndex = isoString.index("+")
		if plusIndex != -1:
			isoString = isoString[:plusIndex]
		content["startDateTime"] = isoString +".000Z"
	if "content" in content and isinstance(content["content"],list):
		#todo: really we have to check if it's vod or linear, but for now this is good enough
		for event in content["content"]:
			handleMedia(event, False, True)
	else:
		handleMedia(content)
	#except Exception, err:
	#	print Exception, err
	
def createUrlSet(fileName):
	urlSet=set()
	with open(fileName) as data_file:
		for line in data_file:
			if "ctap/r1.2.0" in line:
				startIndex = line.find("https://")
				if startIndex == -1:
					continue
				line = line[startIndex:]
				endIndex = line.find(" ")
				if endIndex == -1:
					endIndex = line.find("/n");
				url = line[:endIndex]
				urlSet.add(url)
	return urlSet	

def downloadContentInstance(url, gridDict, downloadDate):
	CTAPindex = url.index("ctap/r1.2.0")
	ctapUrl = url[:CTAPindex]
	print ctapUrl
	services = gridDict["channels"]
	for service in services:
		try:
			contents = service["schedule"]#["events"]
			for content in contents:
				print content["id"]
				contentInstanceUrl = ctapUrl+"ctap/r1.2.0/contentInstances/"+urllib.quote(content["id"],safe='')
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
				#no need for all the content instances, only download one
				return
		except Exception, err:
			print "downloadContentInstance"
			print service
			print Exception, err
			exit(1)
		
def normalizeUrls(urlSet):
	newUrls = set()
	for url in urlSet:
		normalizedUrl = url.replace('sesguard','agr').replace('https://', 'http://').replace('.com/', '.com:8000/')
		if normalizedUrl.endswith(','):
			normalizedUrl = normalizedUrl[:-1]
		newUrls.add(normalizedUrl)
	return newUrls

def downloadImages(obj):
	if isinstance(obj,list):
		for entry in obj:
			downloadImages(entry)
	elif isinstance(obj, dict):
		for key in obj:
			downloadImages(obj[key])
	elif isinstance(obj, str) or isinstance(obj,unicode):
		#print obj
		if obj.endswith(".png") or obj.endswith(".jpg"):
			print "downloading "+ obj
			#fileName=obj.replace("/","_").replace(":","_") + ".img"
			fileName = obj.split("/")[-1]
			download(obj, jsonDir+imagesDir+fileName)

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
	if not os.path.exists(jsonDir+imagesDir):
		os.makedirs(jsonDir+imagesDir)
	urlSet = createUrlSet(logFile)
	#print urlSet
	#exit(0)
	urlSet = normalizeUrls(urlSet)
	#print urlSet
	#urlSet=[]
	for url in urlSet:
		#get url parts
		pathComponents = url.split("?")
		pathComponents = pathComponents[0].split("/")+pathComponents[1:]
		indexOfStart=pathComponents[-1].find("startDateTime")
		if indexOfStart!=-1:
			indexEnd=pathComponents[-1][indexOfStart:].index("&")
			normalizedStr = pathComponents[-1][0:indexOfStart]+"startDateTime=0"+pathComponents[-1][indexOfStart+indexEnd:]
			pathComponents[-1] = normalizedStr
		#make the request be whole days
		indexOfDuration = pathComponents[-1].find("duration")
		if indexOfDuration!=-1:
			indexEnd=pathComponents[-1][indexOfDuration:].find("&")
			if indexEnd==-1:
				normalizedStr = pathComponents[-1][0:indexOfDuration]+"duration="+str(60*60*24)
			else:
				normalizedStr = pathComponents[-1][0:indexOfDuration]+"duration="+str(60*60*24)+pathComponents[-1][indexOfDuration+indexEnd:]
			pathComponents[-1] = normalizedStr
		postFixUrl = "#".join(pathComponents[5:])
		responseFileName = jsonDir+"/"+postFixUrl+".json"
		if os.path.exists(responseFileName):
			print "not downloading " + url +", file already exists"
			continue
		print "downloading "+url+" into : " + responseFileName
		downloadDate = calendar.timegm(time.gmtime())
		responseFileName=download(url, responseFileName)
		if not responseFileName:
			print "!!!!!  something wrong for url " + url
			continue
		print pathComponents
		if "channels" in pathComponents:
			print "channels API"
			with open(responseFileName, "r+") as data_file:
				#download channel logos
				contentsDict = json.load(data_file)
				normalizeGrid(contentsDict, downloadDate)
				data_file.seek(0)
				json.dump(contentsDict, data_file)
				data_file.truncate()
		elif "grid" in pathComponents:
			with open(responseFileName, "r+") as data_file:    
				#normalize the entries and download the content instance for each instance
				contentsDict = json.load(data_file)
				downloadContentInstance(url, contentsDict, downloadDate)
				normalizeGrid(contentsDict, downloadDate)
				data_file.seek(0)
				json.dump(contentsDict, data_file)
				data_file.truncate()
		elif "contentInstances" in pathComponents:
			with open(responseFileName, "r+") as data_file:
				#normalize the entries and download the content instance for each instance
				contentsDict = json.load(data_file)
				normalizeInstance(contentsDict, downloadDate)
				data_file.seek(0)
				json.dump(contentsDict, data_file)
				data_file.truncate()
		elif "categories" in pathComponents:
			with open(responseFileName, "r+") as data_file:
				#download images for vod content
				contentsDict = json.load(data_file)
				downloadImages(contentsDict)
				data_file.seek(0)
				json.dump(contentsDict, data_file)
				data_file.truncate()
	#create generic files for
	print "create generic files"
	os.chdir(jsonDir)
	duration=0
	limit=0
	bestFileGrid=None
	ltvInstance=None
	vodInstance=None
	vodSisInstance=None
	suggestions=None
	cateories=None
	categoriesSis=None
	contentForQuery=None
	vodContent=None
	vodSisContent=None
	for i in os.listdir(os.getcwd()):
		print i
		if i.find("grid") != -1:
			limitLoc=i.find("limit=")
			if limitLoc!=-1:
				limitEnd=i[limitLoc:].find("&")
				limitStr=i[limitLoc+len("limit="):limitLoc+limitEnd]
				curLimit=int(limitStr)
				print "limit is " + str(curLimit)
			durationLoc=i.find("duration=")
			if durationLoc!=-1:
				durationEnd=i[durationLoc:].find("&")
				if durationEnd==-1:
					durationEnd=i[durationLoc:].find(".json")
				durationStr=i[durationLoc+len("duration="):durationLoc+durationEnd]
				curDuration=int(durationStr)
				print "duration is " + str(curDuration)
			if curDuration>=duration and curLimit>=limit:
				duration=curDuration
				limit=curLimit
				bestFileGrid=i
		if i.find("contentInstances")!=-1:
			if not ltvInstance and i.find("%7Eltv")!=-1:
				ltvInstance=i
			elif not vodSisInstance and i.find("~vod")!=-1 and i.find("SIS")!=-1:
				vodSisInstance=i
			elif not vodInstance and i.find("~vod")!=-1:
				vodInstance=i
			elif not contentForQuery and i.find("q=")!=-1:
				contentForQuery=i
			elif not vodContent and i.find("source=vod")!=-1 and i.find("SIS")==-1:
				vodContent = i
			elif not vodSisContent and i.find("source=vod")!=-1 and i.find("SIS")!=-1:
				vodSisContent = i
		if not suggestions and i.find("suggest")!=-1:
			suggestions=i
		if i.find("categories")!=-1:
			if not categoriesSis and i.find("SIS")!=-1:
				categoriesSis=i
			elif not cateories and i.find("SIS")==-1:
				cateories=i
	#agg#grid,
	#find best grid file (longest duration and limit)
	if bestFileGrid:
		shutil.copy(bestFileGrid,"agg#grid.json")
	#contentInstances#ltv,
	if ltvInstance:
		shutil.copy(ltvInstance,"contentInstances#ltv.json")
	#contentInstances#vod
	if vodInstance:
		shutil.copy(vodInstance, "contentInstances#vod.json")
	#contentInstances#SISvod
	if vodSisInstance:
		shutil.copy(vodSisInstance, "contentInstances#SISvod.json")
	#keywords#suggest
	if suggestions:
		shutil.copy(suggestions,"keywords#suggest.json")
	#contentInstances#q
	if contentForQuery:
		shutil.copy(contentForQuery,"contentInstances#q.json")
	#contentInstances#source=vod
	if vodContent:
		shutil.copy(vodContent,"contentInstances#source=vod.json")
	#contentInstances#source=vod
	if vodSisContent:
		shutil.copy(vodSisContent,"contentInstances#source=vodSIS.json")
	#categories#SIS
	if categoriesSis:
		shutil.copy(categoriesSis,"categories#sis.json")
	#categories#x
	if cateories:
		shutil.copy(cateories,"categories#x.json")


main(sys.argv)