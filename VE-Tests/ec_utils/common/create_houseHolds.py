import requests
import httplib
import logging
import json
import os
import sys
import random
import urllib
import termcolor
from optparse import OptionParser,OptionGroup

try:
    from vgw_test_utils.settings import Settings
    from vgw_test_utils.headend_util import headend
    vgw_test_utils_installed = True
except ImportError:
    vgw_test_utils_installed = False

print "vgw_test_util" , vgw_test_utils_installed


level = os.environ.get('LOG_LEVEL', 'INFO')
logging.basicConfig(level=level, format="^%(asctime)s !%(levelname)s <t:%(threadName)s T:%(name)s M:%(filename)s F:%(funcName)s L:%(lineno)d > %(message)s", datefmt="%y/%m/%d %H:%M:%S")
logging.getLogger("requests").setLevel(logging.DEBUG)


def createHouseHold(hhId, login):
    cprint('create new HouseHold: %s Login: %s' % (hhId, login))
    auxHouseholdId = 'aux_'+hhId
    hh_create_request = {
        "householdId" : hhId,
        "accountId" : login,
        "auxHouseholdId" : auxHouseholdId,
        "locale" : {
            "region": region,
            "cmdcRegion": cmdcRegion
        },
        "credentials" : [{
            "login" : login,
            "password" : "1234"
        }]
    }

    headers = {'Source-Type':'STB', 'Source-ID':'123', 'Content-Type':'application/json'}
    url = UPM_URL + 'households/' + hhId
    r = requests.put(url, data = json.dumps(hh_create_request), headers = headers)

    assert r.status_code == httplib.CREATED, "Failed to create houseHold:\n%s" %r.text
    setParentalRatingThreshold(hhId, '18')
    setYouthPin(hhId, '0000')
    setParentalRatingPin(hhId, '0000')
    set_households_device_quota(hhId, 40)

def getHouseHold(hhId):
    url = UPM_URL + 'households/' + hhId
    headers = {'Connection':'close', 'Accept-Encoding':'gzip,deflate', 'Source-Type':'STB', 'Source-ID':'123', 'accept':'application/json'}
    r = requests.get(url, headers=headers)
    return r

def getCatalogueId(platform):
    cprint("getCatalogId for platform %s" % platform)
    url = CMDC_URL + 'region/' + cmdcRegion + '/device/' + platform + '/catalogueId'
    r = requests.get(url)
    assert r.status_code == httplib.OK, "Failed to get CatalogueId:\n%s" %r.text
    dictReply = json.loads(r.text)
    return dictReply['catalogueId']['id']

def isHouseHoldExist(hhId):
    hh = getHouseHold(hhId)
    if hh.status_code == httplib.OK:
        return True
    elif hh.status_code == httplib.NOT_FOUND:
        return False
    assert False, "Failed to get HouseHold. status=%s" %hh.status_code

def deleteHouseHold(hhId):
    cprint("deleting household %s" % hhId)
    url = UPM_URL + 'households/' + hhId
    headers = {'Accept-Encoding':'gzip,deflate', 'Source-Type':'STB', 'Source-ID':'123'}
    cprint('delete HouseHold %s' % (hhId))
    r = requests.delete(url, headers=headers)
    assert r.status_code == httplib.OK, "Failed to delete houseHold:\n%s" %r.text

def setHouseHoldAuthorization(hhId, offersIds, authorizationType='SUB' ,remove=False):
    offersIds = list(set(offersIds))
    url = UPM_URL + 'households/' + hhId + '/authorizations/subscriptions/'
    headers = {'Source-Type':'STB','Source-ID':'123','Content-Type':'application/json'}

    if remove:
        cprint('Removing offers %s to HouseHold %s' % (offersIds, hhId))
    else:
        cprint('Adding %s offers %s to HouseHold %s' % (authorizationType, offersIds, hhId))

    for offerId in offersIds:
        reqBody = {"authorizationId": str(offerId), "authorizationType": "SUBSCRIPTION"}
        urlOffer = str(offerId)

        if authorizationType == 'TITLE':
            reqBody['authorizationStatus'] = "PURCHASE_COMPLETED"

        if remove == False:
            r = requests.put(url + urlOffer ,data =json.dumps(reqBody), headers=headers)
            assert r.status_code == httplib.CREATED, "Failed to add offers to houseHold:\n%s" %r.text
        else:
            r = requests.delete(url + urlOffer ,data =json.dumps(reqBody), headers=headers)
            assert r.status_code == httplib.OK, "Failed to remove offers from houseHold:\n%s" %r.text

def setParentalRatingThreshold(hhId, rating):
    cprint("setParentalRatiingThreshold %s %s" % (hhId,rating))
    url = UPM_URL + 'households/' + hhId + '/userProfiles/' + hhId + '_0/preferences/parentalRatingThreshold'
    headers = {'Source-Type':'SMS','Source-ID':'123', 'Accept': 'text/plain', 'Content-Type': 'text/plain'}
    cprint('Setting  ParentalRatingThreshold = %s to HouseHold %s' % (rating,hhId))
    r = requests.put(url, data = rating, headers=headers)
    assert  (r.status_code == httplib.CREATED or r.status_code == httplib.OK), "Failed to set parental rating to houseHold:\n%s" %r.text




def setParentalRatingPin(hhId, parentalRatingPin):
    cprint('Setting  parentalRatingPin = %s to HouseHold %s' % (parentalRatingPin,hhId))
    url = UPM_URL + 'households/' + hhId + '/preferences/parentalRatingPin'
    headers = {'Source-Type':'SMS','Source-ID':'123', 'Content-Type': 'text/plain'}
    r = requests.put(url, data = parentalRatingPin, headers=headers)
    assert r.status_code == httplib.OK, "Failed to set parental rating to houseHold:\n%s" %r.text



def setYouthPin(hhId, youthProtectionPin):
    cprint("setYouthPin %s %s" % (hhId,youthProtectionPin)) 
    url = UPM_URL + 'households/' + hhId + '/preferences/youthProtectionPin'
    headers = {'Source-Type':'SMS','Source-ID':'123', 'Content-Type': 'text/plain'}
    cprint('Setting  youthProtectionPin = %s to HouseHold %s' % (youthProtectionPin,hhId))
    r = requests.put(url, data = youthProtectionPin, headers=headers)
    assert r.status_code == httplib.OK, "Failed to set parental rating to houseHold:\n%s" %r.text



def set_households_device_quota(hhId, quota):
    cprint("set_househods_device_quota %s %s" % (hhId,quota)) 

    url = UPM_URL + 'households/' + hhId  + '/deviceQuota/'
    device_quata = json.dumps({ "COMPANION":  quota })
    headers = {'Source-Type':'EPG-SERVER','Source-ID':'123','Content-Type':'application/json'}
    r = requests.put(url,data = device_quata, headers=headers)
    assert (r.status_code == httplib.CREATED or r.status_code == httplib.OK), "Failed to set deviceQuota. status=%s\n%s"%(r.status_code,r.text)

def addDeviceToHouseHold(hhId, deviceId, deviceFullType = "Android-Phone"):
    url = UPM_URL + 'households/' + hhId + '/devices/'
    headers = {'Source-Type':'EPG-SERVER','Source-ID':'123','Content-Type':'application/json'}
    cprint('Adding device %s to HouseHold %s , deviceFullType %s' % (deviceId,hhId,deviceFullType))
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
        "drmDeviceType" : "ANDROID",
        "deviceFeatures": ["STB", "PVR", "GATEWAY", "RDK", "HEADED-GATEWAY", "QAM", "IP-CLIENT", "GATEWAY-AVT-CLIENT",
                           "VGS", "5-TUNER"]
    }
    r = requests.put(url + deviceId ,data = json.dumps(add_device_request), headers=headers)
    assert r.status_code == httplib.CREATED, "Failed to add device to houseHold:\n%s" %r.text

def get_offers_from_cmdc(platform):
    sub_offers = []
    title_offers = []
    
    sub_offers_vod, title_offers_vod = get_offers(platform, 'contents')
    sub_offers_linear, title_offers_linear = get_offers(platform, 'services')
    sub_offers = sub_offers_vod + sub_offers_linear
    title_offers = title_offers_vod #only vod has title offers
    
    return sub_offers, title_offers

def get_offers(platform, type):
    catalogueId = getCatalogueId(platform)
    if type == 'contents':
        cmdcContentUrl = CMDC_URL + 'content?catalogueId=' + catalogueId + '&count=255&direction=forward&skipIndex=1'
    else:    
        cmdcContentUrl = CMDC_URL + 'services?region=' + cmdcRegion + '&serviceDeliveryType=abr&count=255&direction=forward&skipIndex=1'

        
    locator = None
    sub_offers = []
    title_offers = []

    while True:
        url = cmdcContentUrl
        if locator:
            url = url + '&' + locator
        r = requests.get(url)
        if r.status_code == httplib.NOT_FOUND:
            break
        #commented due to bug in CMDC. it returns 500
        #assert r.status_code == httplib.OK, "Failed to get content info from cmdc. url = %s status = %s body=%s"%(url, r.status_code, r.text)
        dictReply = json.loads(r.text)
        contents = dictReply[type]
        locator = contents[len(contents) - 1]['locator']
        locator = urllib.urlencode({"locator":locator})
        for content in contents:
            if 'offerIdList' in content:
                #title are only for VOD 
                if type == 'contents' and content['contentNdsDrmAttributes']['isSubscription'] == False:
                    title_offers = list(set(title_offers)|set(content['offerIdList']))
                else:
                    sub_offers = list(set(sub_offers)|set(content['offerIdList']))
        if len(contents) == 1:
            break

    return sub_offers, title_offers

def create_houseHolds(platform):
    sub_offers, title_offers = get_offers_from_cmdc(platform)
    if platform == 'ANDROID':
        rng = range(21,41)
    else:
        rng = range(1,21)
    for i in rng:
        hhid = 'h' + str(i)
        login = 'a' + str(i)

        if isHouseHoldExist(hhid):
            deleteHouseHold(hhid)
        createHouseHold(hhid, login)
        setHouseHoldAuthorization(hhid, sub_offers, authorizationType='SUB')
        if hhid=='h26' or hhid=='h6':
            setHouseHoldAuthorization(hhid, title_offers, authorizationType='TITLE')
        if vgw_test_utils_installed:
            add_channel_sub(hhid)

def add_channel_sub(household_id):

    Settings['household_id'] = household_id
    url = "{0}BillingAdaptor/api/household/{household_id}/authorization/subscription/offerKey".format(BOA_URL, household_id=household_id)

    boa_headers = {
        "Content-Type": "text/xml"
    }

    for offer_key in ('SUB1', 'SUB3', 'SUB7', 'SUB9'):
            data = """<boa:CreateHouseholdSubscription xmlns:boa = "http://protocols.cisco.com/spvtg/boa/commonapi" xmlns:xsi = "http://www.w3.org/2001/XMLSchema-instance">
                                    <subscription>
                                            <offerKey>%s</offerKey>
                                            <authorizationType>SUBSCRIPTION</authorizationType>
                                            <authorizationStatus>PURCHASE_COMPLETED</authorizationStatus>
                                    </subscription>
                              </boa:CreateHouseholdSubscription>""" % offer_key

            r = headend.session.post(url, headers=boa_headers, data=data)
            cprint("status code for offer key %s is %d", offer_key, r.status_code)
            try:
                assert r.status_code == 201, "expect 201 status code. got %s with %s" % (r.status_code, url)
            except AssertionError:
                logging.warning("Error creating offer %s via BOA; return was %s:%s", offer_key, r.status_code, r.text)





def create_household(hh_id,login,platform,sub_offers,title_offers,delete_only=False):
    if isHouseHoldExist(hh_id):
        deleteHouseHold(hh_id)
    if delete_only:
        return
    createHouseHold(hh_id, login)
    setHouseHoldAuthorization(hh_id, sub_offers, authorizationType='SUB')
    if options.show_hh:
        cprint("-Going to show households: %s " % (hh_id))
        r=getHouseHold(hh_id)
        if r.status_code != 200:
            raise Excception("failed to get upm household %s" % hh_id)
        data=json.loads(r.content)
        cprint(json.dumps(data,indent=2))



def create_default_houseHolds(platform):
    sub_offers, title_offers = get_offers_from_cmdc(platform)
    if platform == 'ANDROID':
        rng = range(21,41)
    else:
        rng = range(1,21)
    for i in rng:
        hhid = 'h' + str(i)
        login = 'a' + str(i)
        create_household(hhid, login,platform,sub_offers,title_offers,delete_only=False)
        if hhid=='h26' or hhid=='h6':
            setHouseHoldAuthorization(hhid, title_offers, authorizationType='TITLE')
        if hhid == "h6":
            addDeviceToHouseHold('h6', '123')
        if hhid=="h26":
            addDeviceToHouseHold('h26', '1234')

    

def cprint(message,color='blue'):
    
    if sys.stdout.isatty():
        print termcolor.colored(message,color=color)
    else:
        logging.info(message)
    


def main():
    try:
        if vgw_test_utils_installed:
            cprint("setting up vgw_test_utils")
            Settings.populate()
            Settings.setup_ssh()

        ## create default users
        if not options.hh_prefix:
            cprint("Going to create default households:")
            cprint("IOS : h1 ~ h20")
            cprint("Android : h21 ~ h40")
            cprint("login : a[number]")
            cprint("password: 1234")
            create_default_houseHolds('IOS')
            create_default_houseHolds('ANDROID')
            sys.exit(0)

        if not options.platform:
            cprint("please proivde platform -p ios or -p andorid")
            sys.exit(1)
        

        ## create customerized users
        cprint("Going to create customerized households:")

        try:
            min_range,max_range=options.hh_range.split("~")
            min_range=int(min_range)
            max_range=int(max_range) + 1
        except:
            cprint("incorrect -r range syntax , examples : please use something like   -r 1~1 or -r 2~5",'red')
            print usage
            sys.exit(1) 


        platform=options.platform
        if not platform or platform.lower() not in [ 'ios','android' ] :
            cprint( "ERROR: Please provide platform with eitehr -p ios or -p android",'red')
            print usage
            sys.exit(1)

        sub_offers, title_offers = get_offers_from_cmdc(platform.upper())

        for id in range(min_range,max_range):
            if id == 0:
                id=""
            hh_id=options.hh_prefix + str(id)
            login=hh_id
            create_household(hh_id,login,platform.upper(),sub_offers,title_offers,delete_only=options.delete_only)

    finally:
             if vgw_test_utils_installed:
                 cprint("cleanup vgw_test_utils")
                 Settings.teardown_ssh()

    


###########################################
# MAIN
###########################################


usage="%s [-s prefix]  [ -r 1~5 ] [ -p <platform> ] [lab] " %  sys.argv[0]
usage += "\nExamples:"
usage += termcolor.colored("\n\n-To create users on 'veop' HE :  h1-h21 for ios , h21-h24 for andriod",'blue')
usage += "\n ex: python %s" % (sys.argv[0])
usage += termcolor.colored("\n\n-To create users on any HE , When run scripts from HE deployer:",'blue')
usage += "\n ex: python %s -v -s cannie -p ios deployer ( create single household 'cannie' with ios offers )" % (sys.argv[0])

usage += "\n ex: python %s [-v] -s h -r 21~40 -p andriod deployer ( create h21-h40 with andriod offer)" % (sys.argv[0])

usage += termcolor.colored("\n\n-To create users on any HE, When run scripts from from local PC:",'blue')
usage += "\nNote: you can use 'sudo killall ssh' to termiate all ssh from the terminal"
usage += "\n# ssh -L 6040:im-UPM-UPM.node.vci:6040 -L 8080:boa-boa-rest.node.vci:8080 -L 5600:cm-delivery-CMDC.node.vci:5600 vcidev@jump.openstack-lwr-luke.phx.cisco.com -N -f"
usage += "\n# export CMDC_URL=http://localhost:5600/cmdc/;"
usage += "export UPM_URL=http://localhost:6040/upm/;"
usage += "export BOA_URL=http://localhost:8080/;"
usage += "export cmdcRegion=16384~16385;"
usage += "\nex: python %s [-v ] -s h -r 1~20 -p android" % (sys.argv[0])
usage += "\nex: python %s [-v ] -s h -r 21~40 -p ios" % (sys.argv[0])



parser = OptionParser(usage)
group2=OptionGroup(parser,"For customerized users:")
group2.add_option("-s", "--hh_prefix", dest="hh_prefix",default=None, help="household prefix. any string")
group2.add_option("-r", "--hh_range", dest="hh_range",default='0~0', help="optional. create a range of households, can be something like 2~20")
group2.add_option("-d", "--delete_only ", dest="delete_only", action="store_true", default=False, help="delete households without create")
group2.add_option("-p", "--platform ", dest="platform", action="store", default=None, help="ios or android")
group2.add_option("-v", "--show_hh ", dest="show_hh", action="store_true", default=True, help="show hh after creation")
parser.add_option_group(group2)


(options, args) = parser.parse_args()

#Main
region = "1"
try:
    lab=args.pop(0)
except:
    lab='veop'

if lab.startswith ('openstack') :
    UPM_URL = 'http://im-upm-upm.' + lab + '.phx.cisco.com:6040/upm/'
    CMDC_URL = 'http://cm-delivery-cmdc.' + lab + '.phx.cisco.com:5600/cmdc/'
    BOA_URL = 'http://boa-boa-rest.' + lab + '.phx.cisco.com:8080/'
    cmdcRegion = "16384~16385"

elif lab.startswith('deployer'):
    UPM_URL = 'http://im-upm-upm.node.vci:6040/upm/'
    CMDC_URL = 'http://cm-delivery-cmdc.node.vci:5600/cmdc/'
    BOA_URL = 'http://boa-boa-rest.node.vci:8080/'
    cmdcRegion = "16384~16385"
else:
    UPM_URL = 'http://sgw.' + lab + '.phx.cisco.com:8081/upm/'
    CMDC_URL = 'http://sgw.' + lab + '.phx.cisco.com:8081/cmdc/'
    BOA_URL = 'http://boa.' + lab + '.phx.cisco.com:8080/'
    cmdcRegion = "16384~16385"



## url overwrites    
if os.getenv('UPM_URL'):
    UPM_URL=os.getenv('UPM_URL')
if os.getenv('CMDC_URL'):
    CMDC_URL=os.getenv('CMDC_URL')
if os.getenv('BOA_URL'):
    BOA_URL=os.getenv('BOA_URL')
if os.getenv('cmdcRegion'):
    cmdcRegion=os.getenv('cmdcRegion')

cprint (options)
cprint("lab : %s" % lab)
cprint("UPM_URL: %s" % UPM_URL)
cprint("CMDC_URL: %s" % CMDC_URL)
cprint("BOA_URL: %s" % BOA_URL)
cprint("cmdcRegion: %s" % cmdcRegion)

if __name__ == "__main__":
    main()
