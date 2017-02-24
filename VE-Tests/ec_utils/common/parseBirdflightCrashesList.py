import requests
import httplib
import urllib
import json
import os
import sys

def getReports(url, auth, lastCheckedCrashId):
	nextPage = 1
	lastPage = 1
	lastId = 0
	
	while nextPage <= lastPage:
		print "Next page:" + str(nextPage) + ", last page: " + str(lastPage)
		print "The next url:" + url + "&page=" + str(nextPage)
		r = requests.get(url + "&page=" + str(nextPage))
		assert r.status_code == httplib.OK, "Failed to get list of crash reports. url = %s status = %s body=%s"%(url, r.status_code, r.text)
		dictReply = json.loads(r.text)
		items = dictReply["items"]
		for item in items:
			lastId = item["id"]
			if lastId > lastCheckedCrashId or lastCheckedCrashId == 0:
				href = item["_links"]["download_url"]["href"]
				print "href:" + href
				crashReport = urllib.URLopener()
				crashReport.retrieve(href + auth, str(item["id"]) + ".txt")
		if "next" in dictReply["pagination_data"]:
			nextPage = dictReply["pagination_data"]["next"]
		else:
			nextPage += 1
		lastPage = dictReply["pagination_data"]["last"]
	if lastId > 0:
		with open('lastId.txt', 'wb') as fh:
			fh.write(str(lastId))

if __name__ == "__main__":
	getReports(sys.argv[1], sys.argv[2], long(sys.argv[3]))