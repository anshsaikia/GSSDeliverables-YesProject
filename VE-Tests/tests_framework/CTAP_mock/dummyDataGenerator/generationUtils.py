#usage createChannelResponse [fileName] [numberOfChannels]
import sys
import json
import datetime
from random import randint

TIME_SLOT_FOR_GRID = 3*60
channelLogoUris=["http://phx-media-server.phx.cisco.com/LogosPNG/s10035_h3_aa.png",
				"http://phx-media-server.phx.cisco.com/LogosPNG/s14771_h3_aa.png",
				"http://phx-media-server.phx.cisco.com/LogosPNG/s16585_h3_aa.png",
				"http://phx-media-server.phx.cisco.com/LogosPNG/s17663_h3_aa.png",
				"http://phx-media-server.phx.cisco.com/LogosPNG/s18279_h4_aa.png",
				"http://phx-media-server.phx.cisco.com/LogosPNG/s24959_h4_aa.png",
				"http://phx-media-server.phx.cisco.com/LogosPNG/s26883_h4_aa.png",
				"http://phx-media-server.phx.cisco.com/LogosPNG/s28506_h3_aa.png",
				"http://phx-media-server.phx.cisco.com/LogosPNG/s33668_h3_aa.png",
				"http://phx-media-server.phx.cisco.com/LogosPNG/s50747_h3_aa.png",
				"http://phx-media-server.phx.cisco.com/LogosPNG/s56905_h3_aa.png",
				"http://phx-media-server.phx.cisco.com/LogosPNG/s58649_h3_aa.png",
				"http://phx-media-server.phx.cisco.com/LogosPNG/s59368_h4_aa.png",
				"http://phx-media-server.phx.cisco.com/LogosPNG/s82541_h4_aa.png"]
numOfChannelLogos=14
CHANNELS_PER_PAGE=255

generatedChannels=0

def timeStringFromEpochTime(epochTime):
	isoString = datetime.datetime.fromtimestamp(epochTime).isoformat()
	return isoString +".000Z"

def generateChannels(numOfChannels):
	global generatedChannels
	channelArr = []
	for i in range(generatedChannels+1,generatedChannels+int(numOfChannels)+1):
		channel=dict(id=str(i+100), 
						channelName = "channel_name_"+str(i), 
						logicalChannelNumber = i, 
						isFavorite = i%2, 
						logos = [
							dict(
								size = "vect", 
								type = "regular", 
								mimeType = "image/png", 
								uri = channelLogoUris[i%numOfChannelLogos])]) 
		channelArr.append(channel)
	generatedChannels = generatedChannels+int(numOfChannels)
	return channelArr
	
def generateChannelResponse(numOfChannels,total):
	channelsArr = generateChannels(numOfChannels)
	channelResp = dict( count = int(numOfChannels),
						total = int(total),
						channels = channelsArr)
	response = json.dumps(channelResp)
	return response
	
def createChannelResponse(fileName, numOfChannels):
	if fileName.endswith(".json"):
		fileName=fileName[0:-5]
	numOfRemainingChannels = int(numOfChannels)
	fileNum = 0
	while numOfRemainingChannels>0:
		nowGenerating=min(numOfRemainingChannels,CHANNELS_PER_PAGE)
		print "now generating " + str(nowGenerating) + " channels"
		response = generateChannelResponse(nowGenerating,numOfChannels)
		numOfRemainingChannels = numOfRemainingChannels-nowGenerating
		if fileNum==0 and numOfRemainingChannels<=0:
			fileToWrite=fileName+".json"
		else:
			fileNum=fileNum+1
			fileToWrite=fileName+"_"+str(fileNum)+".json"
		with open(fileToWrite,"w") as data_file:
			data_file.write(response)
			data_file.truncate()

parental=1
contentId=10000
imageId=1
minDuration=5 #5 minutes
maxDuration=60 #1 hour
def generateContentForChannel(channel):
	global contentId, parental, imageId
	contentArr=[]
	remainingDuration=TIME_SLOT_FOR_GRID
	i=0
	while remainingDuration>0 and i<5:
		i = i+1
		contentDuration = randint(minDuration, maxDuration);
		if remainingDuration == TIME_SLOT_FOR_GRID:
			contentStart = -1*randint(0, contentDuration-1)
		else:
			contentStart = TIME_SLOT_FOR_GRID - remainingDuration
		name = channel["channelName"]+"_event_"+str(contentId)
		content = dict(assetType = "broadcastTv",
					parentalRating = parental,
					title = name,
					contentId = "programid://"+str(contentId),
					shortSynopsis = name+"_synopsis",
					startTime = timeStringFromEpochTime(contentStart*60),
					duration = contentDuration*60*1000,
					type = "standalone",
					id = "programid://"+str(contentId)+"~programid://"+str(contentId*3),
					thumbnails = [
						dict(mimeType= "image/jpeg",
						width= 240,
						size= "small",
						uri= "http://phx-media-server.phx.cisco.com/LTVposters/poster%03d_eng.jpg"%imageId,
						height= 13),
						dict(mimeType= "image/jpeg",
						width= 240,
						size= "large",
						uri= "http://phx-media-server.phx.cisco.com/LTVposters/sposter%03d_eng.jpg"%imageId,
						height= 135)]
						)	
		contentArr.append(content)
		contentId = contentId+1
		parental = (parental+1)%16
		imageId = imageId%288+1
		remainingDuration = TIME_SLOT_FOR_GRID - (contentStart + contentDuration)
	return contentArr
	
def generateGridResponse(numOfChannels, total):
	channelArr = generateChannels(numOfChannels)
	for channel in channelArr:
		contentArr = generateContentForChannel(channel)
		channel["schedule"] = dict( count = len(contentArr),
									events = contentArr)
	channelResp = dict( count = int(numOfChannels),
						total = int(total),
						channels = channelArr)
	response = json.dumps(channelResp)
	return response

def createGridResponse(fileName, numOfChannels):
	if fileName.endswith(".json"):
		fileName=fileName[0:-5]
	numOfRemainingChannels = int(numOfChannels)
	fileNum = 0
	while numOfRemainingChannels>0:
		nowGenerating=min(numOfRemainingChannels,CHANNELS_PER_PAGE)
		print "now generating " + str(nowGenerating) + " channels"
		response = generateGridResponse(nowGenerating,numOfChannels)
		numOfRemainingChannels = numOfRemainingChannels-nowGenerating
		if fileNum==0 and numOfRemainingChannels<=0:
			fileToWrite=fileName+".json"
		else:
			fileNum=fileNum+1
			fileToWrite=fileName+"_"+str(fileNum)+".json"
		with open(fileToWrite,"w") as data_file:
			data_file.write(response)
			data_file.truncate()
			
def main(args):
	if len(args)>1:
		if args[1] == "createChannelResponse" and len(args)>3:
			createChannelResponse(args[2],args[3])
			exit(0)
		elif args[1] == "createGridResponse" and len(args)>3:
			createGridResponse(args[2], args[3])
			exit(0)
	print "usage: createChannelResponse [fileName] [numberOfChannels] OR createGridResponse [fileName] [numberOfChannels]"
	exit(1)
		
main(sys.argv)
	
	