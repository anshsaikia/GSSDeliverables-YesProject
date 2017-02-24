import requests
import httplib
import logging
import json
import os
import sys
import random

level = os.environ.get('LOG_LEVEL', 'INFO')
logging.basicConfig(level=level, format="^%(asctime)s !%(levelname)s <t:%(threadName)s T:%(name)s M:%(filename)s F:%(funcName)s L:%(lineno)d > %(message)s", datefmt="%y/%m/%d %H:%M:%S")
logging.getLogger("requests").setLevel(logging.WARNING)

if(len(sys.argv) > 1):
    heAddr = sys.argv[1]
    lab = heAddr
    startindex = heAddr.find("agr.")
    if startindex != -1:
        heAddr = heAddr[startindex+4:]
        endIndex = heAddr.index(".")
        if endIndex == -1:
            print "something wrong in HE url"
            sys.exit(1)
        lab = heAddr[:endIndex]
        upmAdd = 'http://upm.' + lab + '.phx.cisco.com:6040/upm/'
    else:
        portIndex = heAddr.find(":",5)
        upmAdd = heAddr[:portIndex]+":6040/upm/"
else:
    lab='veop'
    upmAdd = 'http://upm.' + lab + '.phx.cisco.com:6040/upm/'
print upmAdd

#UPM_URL = 'http://upm.' + lab + '.phx.cisco.com:6040/upm/'
UPM_URL = upmAdd


def createHouseHold(hhId,login, offers):
    logging.info('create new HouseHold: %s Login: %s' % (hhId, login))

    hh_create_request = {
        "householdId" : hhId,
        "accountId" : hhId,
        "locale" : {
            "region": "1",
            "cmdcRegion": "16384~16385"
        },
        "credentials" : [{
            "login" : login,
            "password" : "1234"
        }],
        "devices": [{
            "externalDeviceId" : "102030102030102030",
        	"deviceId" : "102030",
        	"friendlyName" : "Android device",
        	"deviceFeatures":["COMPANION","ABR"],
        	"userId" : "USERNAME",
        	"deviceFullType": "ANDORID-PHONE",
        	"drmDeviceId" : "102030DRM",
        	"accountId" : "h66",
        	"drmDeviceType" : "ANDROID"}]
    }

    headers = {'Source-Type':'STB', 'Source-ID':'123', 'Content-Type':'application/json'}
    url = UPM_URL + 'households/' + hhId
    r = requests.put(url, data = json.dumps(hh_create_request), headers = headers)

    assert r.status_code == httplib.CREATED, "Failed to create houseHold:\n%s" %r.text
    setHouseHoldAuthorization(hhId, offers)
    setYouthPin(hhId,'1234')
    setParentalRatingThreshold(hhId, '18')

def getHouseHold(hhId):
    url = UPM_URL + 'households/' + hhId
    print url
    headers = {'Connection':'close', 'Accept-Encoding':'gzip,deflate', 'Source-Type':'STB', 'Source-ID':'123', 'accept':'application/json'}
    r = requests.get(url, headers=headers)
    return r

def getHouseHoldDevice(hhId,hhDevice):
    url = UPM_URL + 'households/' + hhId + "/devices/" + deviceId
    print url
    headers = {'Connection':'close', 'Accept-Encoding':'gzip,deflate', 'Source-Type':'STB', 'Source-ID':'123', 'accept':'application/json'}
    r = requests.get(url, headers=headers)
    return r

def isHouseHoldExist(hhId):
    hh = getHouseHold(hhId)
    if hh.status_code == httplib.OK:
        return True
    elif hh.status_code == httplib.NOT_FOUND:
        return False
    logging.error("Failed to get HouseHold. status=%s" %hh.status_code)
    assert (False)

def isDeviceExist(hhId, deviceId):
    hh = getHouseHoldDevice(hhId,deviceId)
    if hh.status_code == httplib.OK:
        return True
    elif hh.status_code == httplib.NOT_FOUND:
        return False
    logging.error("Failed to get HouseHold device. status=%s" %hh.status_code)
    assert (False)

def deleteHouseHold(hhId):
    url = UPM_URL + 'households/' + hhId
    headers = {'Accept-Encoding':'gzip,deflate', 'Source-Type':'STB', 'Source-ID':'123'}
    logging.info('delete HouseHold %s' % (hhId))
    r = requests.delete(url, headers=headers)
    assert r.status_code == httplib.OK, "Failed to delete houseHold:\n%s" %r.text

def setHouseHoldAuthorization(hhId, offersIds, remove=False):
    offersIds = list(set(offersIds))
    url = UPM_URL + 'households/' + hhId + '/authorizations/subscriptions/'
    headers = {'Source-Type':'STB','Source-ID':'123','Content-Type':'application/json'}
    if remove:
        logging.info('Removing offers %s to HouseHold %s' % (offersIds, hhId))
    else:
        logging.info('Adding offers %s to HouseHold %s' % (offersIds, hhId))

    for offerId in offersIds:
        reqBody = {"authorizationId" : str(offerId), "authorizationType": "SUBSCRIPTION"}
        if remove == False:
            r = requests.put(url + str(offerId) ,data =json.dumps(reqBody), headers=headers)
            assert r.status_code == httplib.CREATED, "Failed to add offers to houseHold:\n%s" %r.text
        else:
            r = requests.delete(url + str(offerId) ,data =json.dumps(reqBody), headers=headers)
            assert r.status_code == httplib.OK, "Failed to remove offers from houseHold:\n%s" %r.text

def setParentalRatingThreshold(hhId, rating):
    url = UPM_URL + 'households/' + hhId + '/userProfiles/' + hhId + '_0/preferences/parentalRatingThreshold'
    headers = {'Source-Type':'SMS','Source-ID':'123', 'Accept': 'text/plain'}
    logging.info('Setting  ParentalRatingThreshold = %s to HouseHold %s' % (rating,hhId))
    r = requests.put(url, data = rating, headers=headers)
    assert r.status_code == httplib.OK, "Failed to set parental rating to houseHold:\n%s" %r.text

def setYouthPin(hhId, pin):
    url = UPM_URL + 'households/' + hhId + '/preferences/youthProtectionPin'
    headers = {'Source-Type':'SMS','Source-ID':'123', 'Content-Type': 'text/plain'}
    logging.info('Setting  youthProtectionPin = %s to HouseHold %s' % (pin,hhId))
    r = requests.put(url, data = pin, headers=headers)
    assert r.status_code == httplib.OK, "Failed to set parental rating to houseHold:\n%s" %r.text

def addDeviceToHouseHold(hhId, deviceId, deviceFullType = "Android-Phone"):
    url = UPM_URL + 'households/' + hhId + '/devices/'
    print url
    headers = {'Source-Type':'EPG-SERVER','Source-ID':'123','Content-Type':'application/json'}
    logging.info('Adding device %s to HouseHold %s' % (deviceId,hhId))
    extDeviceId = ''
    for i in range(0, 15):
        extDeviceId = extDeviceId + random.choice('1234567890ABCDE')
    add_device_request = {
        "externalDeviceId" : extDeviceId,
        "deviceId" : deviceId,
        "friendlyName" : "Android device",
        "userId" : "USERNAME",
        "deviceFullType": deviceFullType,
        "drmDeviceId" : deviceId + 'DRM',
        "accountId" : hhId,
        "drmDeviceType" : "ANDROID"
    }
    r = requests.post(url + deviceId ,data = json.dumps(add_device_request), headers=headers)
    assert r.status_code == httplib.CREATED, "Failed to add device to houseHold:\n%s" %r.text

#Main    
hhid="h66"
login = "login_h66"
deviceId = "123"
offers = ['1','2','3','4','5','6','7']
if not isHouseHoldExist(hhid):
	createHouseHold(hhid, login, offers)
#if not isDeviceExist(hhid, deviceId):
#	addDeviceToHouseHold(hhid, deviceId) #adding Android phone, but we don't care for now
    
