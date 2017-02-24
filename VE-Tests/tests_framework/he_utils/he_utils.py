import time
from datetime import timedelta
import logging
import json
import httplib

import copy
import random
import datetime
import urllib
from threading import Thread
from enum import Enum
from copy import deepcopy
import xml.etree.ElementTree as ET
import sys
from retrying import retry
from lazy import lazy
import os.path

try:
    from vgw_test_utils.headend_util import reset_household_provisioning
    from vgw_test_utils.settings import Settings
    vgw_test_utils_installed = True
except ImportError:
    vgw_test_utils_installed = False

global ZONE_GEO_ALLOWED, ZONE_NAME_GLOBAL, ZONE_ONNET_ALLOWED, ZONE_BLACKLISTED,ZONE_GEO_CITY_ALLOWED,ZONE_NETWORK_TYPE,ZONE_IN_HOME
global SUBNET, COUNTRY_CODE, ASN,CITY,ON_NET_ASN,GEO_RESTRICTED_IP

ZONE_BLACKLISTED = 'Restrict:Blacklist-IP'
ZONE_GEO_ALLOWED = 'Allow:Geo-Location'
ZONE_GEO_CITY_ALLOWED = "Allow:City"
ZONE_ONNET_ALLOWED = "Allow:SP-OnNet"
ZONE_NETWORK_TYPE = "Requires:WiFi"
ZONE_IN_HOME ="Check:In-Home"
ZONE_NAME_GLOBAL = 'ALL'

SUBNET = 'SubNet'
COUNTRY_CODE = 'CountryCode'
CITY="City"
ASN = 'ASN'
ON_NET_ASN = '31334'
GEO_RESTRICTED_IP = '192.2.22.3'

DEFAULT_PARENTAL_RATING_THRESHOLD = 30
RES_CODE_OK=200

class ServiceDeliveryType(Enum):
    CABLE = "CABLE"
    ABR = "ABR"
    ALL = "ALL"


class VodContentType(Enum):
    ENCRYPTED = "encrypted"
    CLEAR = "clear"
    SVOD = "svod"
    TVOD = "tvod"
    WITH_HIGH_RATED_TRAILER = "with_high_rated_trailer"
    WITH_LOW_RATED_TRAILER = "with_low_rated_trailer"
    HD = "hd"
    SD = "sd"
    EROTIC = "erotic"
    NON_EROTIC = "non_erotic"
    HIGH_RATED = "high_rated"
    LOW_RATED = "low_rated"
    TITLE = "title"


policyOffers = {3: {'policyType': 'totalProvider'},
                4: {'policyType': 'resolutionDeviceType'},
                6: {'policyType': 'totalProvider'},
                7: {'policyType': 'resolutionDeviceType'}}

region = '1'
cmdcMaxCount = 255

class HeUtilsPreloadTypes(Enum):
    vod = "vod"
    linear = "linear"
    cable = "cable"
    abr = "abr"

class HeUtils(object):
    def __init__(self, ve_test):
        logging.info("start HeUtils init")
        self.thread = Thread(target = self.invoke_actions)
        self.step_name = None
        self.exception = None
        self.heUtilsFinished = False
        self.test = ve_test
        self.configuration = ve_test.configuration
        self.preload = None
        self.he_lists = {}
        if self.test.useAltRegion:
            self.cmdcRegion = '76~3'
        else:
            self.cmdcRegion = '16384~16385'

        if self.test.vgwUtils:
            self.cmdcRegion = '{cmdc_region}'.format(**Settings)

        self.ipomUrl = self.urlCreate('ipomIp')
        self.schedUrl = self.urlCreate('sched', '/sched/')
        self.cmdcUrl = self.urlCreate('cmdcIp', '/cmdc/')
        self.bsmUrl = self.urlCreate('bsmIp', '/bsm/OfferDetails')
        self.upmUrl = self.urlCreate('upmIp', '/upm/')
        self.boaUrl = self.urlCreate('boaIp', '/BillingAdaptor/api')
        self.boaUrlv2 = self.urlCreate('boaIp', '/BillingAdaptor/api/v2')
        self.ctapUrl = self.urlCreate('applicationServerIp', '/ctap/')
        self.PrmUrl = self.urlCreate('PrmUrl')
        self.pdsUrl = self.urlCreate('pdsIP', '/cp/pds/v1/policies/')
        self.StreamingSessionPath = '/sm/streamingSession/'
        logging.info('Device IP and port: %s' % self.test.device_ip)
        logging.info('Device ID is : %s' % self.test.device_id)
        self.ApcSessionsUrl = self.urlCreate('ApcSessionsUrl', '/cp/apc/v1/sessions')
        self.configuration["he"]["cmdcRegion"] = self.cmdcRegion
        self.configuration["he"]["region"] = region
        self.configServiceWSDL = '/config/configService?WSDL'
        logging.info('Region = %s, cmdcRegion = %s' % (region,self.cmdcRegion))
        self.houseHolds = []
        self.step_name = None
        self.is_fixed_household = ve_test.is_fixed_household
        self.platform = ve_test.platform
        self.session_guard_header = None
        self.ZONE_BLACKLISTED = ZONE_BLACKLISTED
        self.ZONE_GEO_ALLOWED = ZONE_GEO_ALLOWED
        self.ZONE_ONNET_ALLOWED = ZONE_ONNET_ALLOWED
        self.ZONE_NAME_GLOBAL = ZONE_NAME_GLOBAL
        self.ZONE_GEO_CITY_ALLOWED = ZONE_GEO_CITY_ALLOWED
        self.ZONE_IN_HOME = ZONE_IN_HOME
        self.ZONE_NETWORK_TYPE = ZONE_NETWORK_TYPE
        self.SUBNET = SUBNET
        self.CITY = CITY
        self.COUNTRY_CODE = COUNTRY_CODE
        self.ASN = ASN
        self.YOUTH_LIMIT_RATING = ve_test.screens.pincode.YOUTH_LIMIT_RATING

    def urlCreate(self, configName, suffix=None):
        path = None
        configValue = self.configuration["he"][configName]
        if configValue == None:
            return None
        prefix = 'http://' + configValue
        if suffix:
            path = prefix + suffix
        else:
            path = prefix
        logging.info(configName + " url:" + path)
        return path


    def prepare_step(self, var_name, condition):
        if condition:
            self.step_name = var_name
            logging.info("Preparing step: " + var_name)
            self.exception = "Timeout for step: " + var_name
            getattr(self, var_name)

    @lazy
    def default_credentials(self):
        return self.generate_credentials(self.is_fixed_household)

    @lazy
    def vod_assets(self):
        self.test.log("HE_PROPERTY: Loading VOD Assets")
        assets = self.get_vod_contents_from_cmdc()
        if self.test.verbose:
            logging.debug('Assets:  (%d) \n%s' % (len(assets),json.dumps(assets, indent = 2)))
        if not self.is_fixed_household:
            svod_offers, tvod_offers = self.getVodOffers(assets)
            self.addHHoffers(svod_offers)
        return assets

    @lazy
    def services(self):
        self.test.log("HE_PROPERTY: Loading Linear Assets")
        services = self.get_linear_services_from_cmdc()
        if not self.is_fixed_household:
            offers = self.getServiceOffers(services)
            self.addHHoffers(offers)
        if self.test.verbose:
            logging.debug('Linear Services: (%d) \n%s' % (len(services),json.dumps(services, indent = 2)))
        return services

    @lazy
    def abr_services(self):
        self.test.log("HE_PROPERTY: Loading Abr Services")
        abr_services = self.get_linear_services_from_cmdc(ServiceDeliveryType.ABR)
        return abr_services

    @lazy
    def abr_services_sorted(self):
        self.test.log("HE_PROPERTY: Loading Services Sorted")
        abr_services_sorted = sorted(self.abr_services.iteritems(), key=lambda (x, y): y['logicalChannelNumber'])
        if self.test.verbose:
            logging.debug('ABR Services: (%d) \n%s' % (len(abr_services_sorted),json.dumps(abr_services_sorted, indent = 2)))
        return abr_services_sorted

    @lazy
    def cable_services(self):
        self.test.log("HE_PROPERTY: Loading Cable Services")
        cable_services = self.get_linear_services_from_cmdc(ServiceDeliveryType.CABLE)
        if self.test.verbose:
            logging.debug('Cable Services: (%d) \n%s' % (len(cable_services),json.dumps(cable_services, indent = 2)))
        return cable_services

    @lazy
    def cable_only_services(self):
        cmdcServicesUrl = self.cmdcUrl + 'services?region=' + self.cmdcRegion
        dictReply = self.send_getRequest(cmdcServicesUrl)
        response_services = dictReply["services"]
        assert dictReply["header"]["total"] > 0
        services_list = self.get_service_info_from_cmdc_service_list(response_services).values()

        #Store IDs of all non-qam channels
        not_qam_channels = [service['serviceEquivalenceKey'] for service in services_list \
                            if 'cable' not in [delivery['type'] for delivery in service['serviceDeliveries']]]

        #Filter all channels with 'cable' delivery type that not in previous list
        cable_only_services = [service for service in services_list \
                                if len(service['serviceDeliveries']) == 1 and 'cable' in service['serviceDeliveries'][0]['type'] \
                                and service['serviceEquivalenceKey'] not in not_qam_channels]

        return cable_only_services

    @lazy
    def ctap_version(self):
        url = self.ctapUrl + 'about'
        logging.debug('getCtapVersion')
        ctapResponse = self.send_getRequest(url)
        logging.info('ctap version: %s ' % ctapResponse['version'])
        version = ctapResponse['version']
        return version

    def preload(self, var_name, assert_msg):
        self.test.log_assert(getattr(self, var_name), assert_msg)

    def invoke_actions(self):
        try:
            self.prepare_step("default_credentials", True)
            self.prepare_step("services", not self.is_fixed_household)
            if self.preload:
                self.prepare_step("vod_assets", "vod" in self.preload)
                self.prepare_step("cable_services", "cable" in self.preload)
                self.prepare_step("cable_only_services", "cable" in self.preload)
                self.prepare_step("abr_services", "abr" in self.preload)

            self.heUtilsFinished = True
        except AssertionError as e:
            self.exception = str(self.step_name) + " failed because of assertion error: "
            self.exception += str(e.args[0])
            logging.exception("************\n\nheadend assert error: " + str(e.args[0]) + "\n\n****************\n\n")
        except KeyError as e:
            self.exception = str(self.step_name) + " failed because of invalid key error: "
            self.exception += str(e.args[0])
            logging.exception("************\n\nheadend key error: " + str(e.args[0]) + "\n\n****************\n\n")
        except Exception as e:
            self.exception = str(self.step_name) + " failed because of: "
            self.exception += str(e)
            logging.exception("************\n\nheadend error: " + str(e) + "\n\n****************\n\n")
        except:
            e = sys.exc_info()[0]
            self.exception = str(self.step_name) + " generically failed because of: "
            self.exception += str(e)
            logging.exception("************\n\nheadend error: " + str(e) + "\n\n****************\n\n")
        '''
        services/assets structure:
        {<asset/service id>:{
            'rating':<rating>,
            'drmType':<none/vgDrm>,
            'url':<playback url>,
            'providerId':<providerId>,
            'offers':[<offers id's>],
            'defaultLang': <default lang>,
            'policy': <policy name>,
            'audioLang': [<audio lang's>],
            'videoFormat': <SD/HD>
            }
        }
        '''

    def get_cmdc_assets(self, catalogueId, classificationId, sort):
        cmdcClassificationsUrl = self.cmdcUrl + 'content?sort=' + sort + '&region' + self.cmdcRegion + '&catalogueId=' + catalogueId +'&classificationId=' + classificationId;

        r = self.test.requests.get(cmdcClassificationsUrl)
        if r.status_code != httplib.OK:
            logging.error("Request from CMDC failed. status = %s" % r.status_code)
            return None
        else:
            return r

    def get_vodUri(self, contentId, offerId):
        catalogueId = self.getCatalogueId(self.platform)
        cmdcVodUrl = self.cmdcUrl + 'content/' + urllib.quote(contentId, '') + '/' + str(offerId) + '/uri?catalogueId=' + catalogueId
        if self.test.verbose:
            logging.debug("url = %s " % cmdcVodUrl)
        r = self.test.requests.get(cmdcVodUrl)
        if r.status_code != httplib.OK:
            logging.warning("Get Vod Url Failed! url = %s status = %s body=%s" % (cmdcVodUrl, r.status_code, r.json()))
            return None
        if self.test.verbose:
            logging.debug('server response: %s' % json.dumps(r.json(), indent = 2))
        dictReply = r.json()
        return dictReply['deliveries'][0]['uri']

    def get_vodBrId(self, offerId):
        requestBody = '{"packet":{"version":"1.0","getOfferDetailsRequest":{"offerId":"'+str(offerId)+ '"}}}'
        r = self.test.requests.post(self.bsmUrl, requestBody)
        if r.status_code != httplib.OK:
            logging.error("getOfferDetailsRequest from BSM failed. status = %s" % r.status_code)
            return None
        #assert r.status_code == httplib.OK, "url = %s status = %s body=%s"%(self.bsmUrl, r.status_code, r.json())
        logging.debug('server response: %s' % json.dumps(r.json(), indent = 2))
        dictReply = r.json()
        brId = dictReply['packet']['getOfferDetailsResponse']['offerDetails'][0]['brId']
        return brId

    def getCatalogueId(self,platform):
        url = self.cmdcUrl + 'region/' + self.cmdcRegion + '/device/' + platform.upper() + '/catalogueId'
        dictReply = self.send_getRequest(url)
        return dictReply['catalogueId']['id']

    def isPolicyOffer(self, offers):
        for offer in offers:
            if offer in policyOffers:
                return policyOffers[offer]['policyType']
        return 'false'

    def parse_url(self, url):
        audios=[]
        subtitles =[]
        defaultLang = None
        isDefault = False
        fromCache = False
        r = None

        try:
            if self.test.useCache:
                in_cache = self.in_url_cache(url)
                cache_response = self.get_url_cache(url, is_json=False)
                if in_cache:
                    if cache_response:
                        fromCache = True
                        r.text = cache_response
                        r.status_code = httplib.OK
                    else:
                        r.status_code = httplib.NO_CONTENT
                else:
                    r = self.test.requests.get(url)
            else:
                r = self.test.requests.get(url)

        except:
            logging.error("Got Exception to get URL %s" % (url))
            if self.test.useCache:
                self.set_url_cache(url, None, is_json=False)
            return {'audios' : audios, '' : subtitles, 'defaultLang' : defaultLang}

        if r.status_code != httplib.OK:
            logging.warn("Failed to get URL %s. status=%s" % (url, r.status_code))
            if self.test.useCache:
                self.set_url_cache(url, None, is_json=False)
            return {'audios' : audios, 'subtitles' : subtitles, 'defaultLang' : defaultLang}

        if not fromCache and self.test.useCache:
            self.set_url_cache(url, r.text, is_json=False)

        nr = r.text.split('#')
        for line in nr:
            if 'TYPE=AUDIO' in line:
                keys = dict()
                for item in line.split(','):
                    key, value = item.split('=')
                    value = value.replace('"', '')
                    value = value.replace('\n', '')
                    keys[key] = value
                    if (key == 'DEFAULT' and value == 'YES'):
                        isDefault = True
                    elif (key == 'DEFAULT' and value == 'NO'):
                        isDefault = False
                    if key == 'LANGUAGE':
                        audios.append(value)
                        if isDefault:
                            defaultLang = value
            if 'TYPE=SUBTITLES' in line:
                keys = dict()
                for item in line.split(','):
                    key, value = item.split('=')
                    value = value.replace('"', '')
                    value = value.replace('\n', '')
                    keys[key] = value
                    if key == 'LANGUAGE':
                        subtitles.append(value)
        res = {
                'audios' : audios,
                'subtitles' : subtitles,
                'defaultLang' : defaultLang
               }
        return res

    def get_current_service_eventEndTime(self, startTime, endTime, serviceId = None, eventCount = None, ignore_series = False, discardEvent=''):
        url = self.cmdcUrl + "services/schedule/" + str(startTime)+"~"+str(endTime)+"?region="+self.cmdcRegion
        if serviceId is not None:
            url += "&serviceList="+str(serviceId)
        if eventCount:
            url += "&eventCount="+str(eventCount)
        result = self.send_getRequest(url, useCache=False)
        eventName = result["services"][0]["contents"][0]["longSynopsis"]
        if ("contents" in result["services"][0]) and (eventName not in discardEvent):
            if "seriesId" in result["services"][0]["contents"][0] and ignore_series:
                return 0, ''
            evenStartTime = result["services"][0]["contents"][0]["broadcastDateTime"]
            evenDuration = result["services"][0]["contents"][0]["duration"]
            eventEndTime = evenStartTime + evenDuration
            return eventEndTime, eventName
        else:
            return 0, ''

    def get_cmdc_logicalChannelNumber_by_serviceId(self, serviceId = None):
        url = self.cmdcUrl + "services?region="+self.cmdcRegion
        if serviceId is not None:
            url += "&serviceList="+str(serviceId)
        result = self.send_getRequest(url)
        return result["services"][0]["logicalChannelNumber"]

    def wait_for_recording_status(self, event_title, status='RECORDING', retries=90):
        from vgw_test_utils.headend_util import get_all_catalog
        filter = "state=" + status
        @retry(stop_max_attempt_number=retries, wait_fixed=500)
        def retry_recording_status():
            catalog = get_all_catalog(filter_to_use=filter)
            for event in catalog:
                if 'content' in event:
                    if event['content']['title'].upper() == event_title.upper():
                        return event
            logging.warning("event:%s is still not in state:%s ...", event_title, status)
            raise KeyError("event:%s is still not in state:%s ...", event_title, status)
        try:
            event = retry_recording_status()
        except:
            self.test.log_assert(False, "Fail to find event:{} in status:{}".format(event_title, status))
        return event

    def get_channel_to_record_current_event(self, remaining_time_minutes=10, tries=10, delay_seconds=60, ignore_series=False, abr_channels=None, discardEvent='', minLogicalChannelNumber=7): #finds a channel on which current event end time is at least 10 minutes away
        for x in xrange(tries):
            if abr_channels is None:
                abr_channels = self.abr_services_sorted
            startTime = int(time.time()) * 1000
            day = int(timedelta(days = 1).total_seconds() * 1000)
            endTime = startTime + day #jump 1 day
            for ch in abr_channels:
                evenEndTime, eventName = self.get_current_service_eventEndTime(startTime=startTime, endTime=endTime, serviceId=ch[0], eventCount=1, ignore_series=ignore_series, discardEvent=discardEvent)
                if (evenEndTime > 0) and ((evenEndTime - startTime) > int(timedelta(minutes = remaining_time_minutes).total_seconds() * 1000)): #if evenEndTime time is more than 10 minutes away
                        logicalChannelNumber = ch[1]["logicalChannelNumber"]
                        if (logicalChannelNumber > minLogicalChannelNumber): # This limit is avoid channels that are too close to the beginning of the guide list
                          return logicalChannelNumber, eventName
            self.test.log('waiting for a channel with remaining {} minutes... (try number {} out of {})'.format(remaining_time_minutes, x, tries))
            self.test.wait(delay_seconds)
        self.test.log_assert(False, 'could not find any channel with remaining {} minutes!'.format(remaining_time_minutes))

    def get_service_info_from_cmdc_service_list(self, serviceList):

        servicesNum = len(serviceList)
        linearServices = {}
        videoFormat = 'hd'

        for i in range(servicesNum):
            linearService = {}
            id = serviceList[i]['id']
            linearService['videoFormat'] = videoFormat
            #if services[i]['serviceNdsDrmAttributes']['isDrmFree']:
            if serviceList[i]['drmProtected']:
                linearService['drmType'] = 'vgDrm'
            else:
                linearService['drmType'] = 'none'
                linearService['providerId'] = serviceList[i]['provider']

            if serviceList[i]['serviceDeliveries'][0]['type'] == 'abr':
                linearService['url'] = serviceList[i]['serviceDeliveries'][0]['uri']
                parsedUrl = self.parse_url(linearService['url'])
                if parsedUrl['audios']:
                    linearService['audioLang'] = parsedUrl['audios']
                if "subtitles" in parsedUrl.keys() and parsedUrl['subtitles']:
                    linearService['subLang'] = parsedUrl['subtitles']
                if parsedUrl['defaultLang']:
                    linearService['defaultLang'] = parsedUrl['defaultLang']
            else: # case of cable
                pass
            if 'parentalRating' in serviceList[i]:
                linearService['rating'] = serviceList[i]['parentalRating']['rating']
            else:
                linearService['rating'] = 0
            linearService['serviceEquivalenceKey'] = serviceList[i]['serviceEquivalenceKey']
            linearService['logicalChannelNumber'] = serviceList[i]['logicalChannelNumber']
            if 'serviceDeliveries' in serviceList[i]:
                linearService['serviceDeliveries'] = deepcopy(serviceList[i]['serviceDeliveries'])
            linearService['id'] = id
            if 'offerIdList' in serviceList[i]:
                linearService['offers'] = serviceList[i]['offerIdList']
                linearService['policy'] = self.isPolicyOffer(linearService['offers'])
                linearServices[id] = linearService
            #video format is not determine per channel, its per event. give random value
            if videoFormat == 'hd':
                videoFormat = 'sd'
            else:
                videoFormat = 'hd'

        return linearServices

    def url_to_file_cache_path(self, url):
        self.test.log_assert(self.test.cacheDir, "Cache directory not set in configuration file (cacheDir)")
        url = url.replace("/", "_")
        url = url.replace("?", "_")
        url = url.replace(":", "_")
        url = url.replace(".", "_")
        url = url.replace("~", "_")
        url = url.replace("=", "_")
        url = url.replace("&", "_")
        path = self.test.cacheDir + "/" + self.test.vgwServerName + "/" + url + ".json"
        return path

    def in_url_cache(self, url):
        filename = self.url_to_file_cache_path(url)
        data = None
        return os.path.exists(filename)

    def get_url_cache(self, url, is_json):
        filename = self.url_to_file_cache_path(url)
        data = None
        if os.path.exists(filename):
            print "using cache for url: " + filename
            with open(filename) as data_file:
                if is_json:
                    data = json.load(data_file)
                else:
                    data = data_file.read()
        return data

    def set_url_cache(self, url, dict, is_json):
        filename = self.url_to_file_cache_path(url)
        self.test.appium.os_cmd("mkdir -p " + self.test.cacheDir + "/" + self.test.vgwServerName, log=False)
        with open(filename, 'w') as outfile:
            if dict:
                if is_json:
                    json.dump(dict, outfile)
                else:
                    outfile.write(dict)

    def send_getRequest(self, url, headers=None, useCache=True):
        if headers == None:
            headers = self.session_guard_header
        if useCache and self.test.useCache:
            dictReply = self.get_url_cache(url, is_json=True)
            if dictReply:
                return dictReply
        if self.test.verbose:
            logging.debug("url = %s header= %s" % (url,headers))
        r = self.test.requests.get(url, headers=headers)
        assert r.status_code == httplib.OK, "url = %s status = %s body=%s" % (url, r.status_code, r.reason)
        if self.test.verbose:
            logging.debug('server response: %s' % json.dumps(r.json(), indent = 2))
        dictReply = r.json()
        if useCache and self.test.useCache:
            self.set_url_cache(url, dictReply, is_json=True)
        return dictReply

    def generate_credentials(self, is_fixed_household = False):
        if not is_fixed_household:
            #only add PVR to HH by default for KD
            hhId, account_id = self.createTestHouseHold(withPVR=(self.test.project == "KD"))
        else:
            hhId = self.configuration["he"]["generated_household"]
            account_id = self.configuration["he"]["generated_username"]
        self.session_guard_header = self.create_session_guard_header(hhId)
        return hhId, account_id

    def get_default_credentials(self):
        return (self.default_credentials[0], self.default_credentials[1])

    def create_session_guard_header(self, hhid):

        if self.test.project_type != "KSTB":
            if self.test.project == "KD":
                sessionInfo = json.dumps({"hhId":hhid, "upId":hhid+'_0', "sessionId":'12345678', "devId":self.test.device_id, "cmdcRegion": self.cmdcRegion,"tenant":"kd","region": region, "deviceFeatures": ["COMPANION", "ABR"],"cmdcDeviceType": self.platform.upper()})
            else:
                sessionInfo = json.dumps({"hhId":hhid, "upId":hhid+'_0', "sessionId":'12345678', "devId":self.test.device_id, "cmdcRegion": self.cmdcRegion,"tenant":"K","region": region, "deviceFeatures": ["COMPANION", "ABR"],"cmdcDeviceType": self.platform.upper()})
        else:
                sessionInfo = json.dumps({"hhId":hhid, "upId":hhid+'_0', "sessionId":'12345678', "devId":Settings["device_id_dummy_companion"], "cmdcRegion": self.cmdcRegion,"tenant":"k","region": region, "deviceFeatures": ["COMPANION", "ABR"],"cmdcDeviceType": self.platform.upper()})
        sessionGuardHeader = {"x-cisco-vcs-identity" :  sessionInfo}
        return sessionGuardHeader

    def get_abr_linear_services_from_cmdc(self):
        return  self.abr_services

    def get_cable_linear_services_from_cmdc(self):
        return  self.cable_services

    # Waiting for CMDC defect fix on grouped channel: returns an empty schedule event.  The group channel should inherit from the master which is cable.
    def get_linear_services_from_cmdc(self, serviceDeliveryType=ServiceDeliveryType.ALL):
        cmdcServicesUrl = self.cmdcUrl + 'services?region=' + self.cmdcRegion
        #TODO: use normalized param after cmdc defect is resolved
        # normalized = '&isNormalized=true'

        if serviceDeliveryType is ServiceDeliveryType.CABLE:
            cmdcServicesUrl +=  '&serviceDeliveryType=cable'
        if serviceDeliveryType is ServiceDeliveryType.ABR:
            cmdcServicesUrl += '&serviceDeliveryType=abr'

        dictReply = self.send_getRequest(cmdcServicesUrl)
        services = dictReply["services"]
        servicesNum = dictReply["header"]["total"]
        assert servicesNum > 0, "Cannot find services! reply is " + str(dictReply)

        linearServices = self.get_service_info_from_cmdc_service_list(services)

        return linearServices

    def set_optional_value(self, var, name, root, *keys):
        key_path = ""
        failed = False
        item = root
        for key in keys:
            if isinstance(item, dict):
                key_path += "['" + str(key) + "']"
                if not (item and key in item):
                    failed = True
                    break
            else:
                key_path += "[" + str(key) + "]"
                if not (item and int(key) < len(item)):
                    failed = True
                    break

            item = item[key]
        if failed:
            if self.test.verbose:
                self.test.log("cannot find path: " + key_path)
        else:
            var[name] = item


    def get_vod_contents_from_cmdc(self):
        catalogueId = self.getCatalogueId(self.platform)
        cmdcContentUrl = self.cmdcUrl + 'content?filter=source~vod&count=' + str(cmdcMaxCount) + '&catalogueId=' + catalogueId
        dictReply = self.send_getRequest(cmdcContentUrl)
        contents = dictReply['contents']
        contentsNum = len(contents)
        if contentsNum > cmdcMaxCount:
            contentsNum = cmdcMaxCount
        assert contentsNum > 0
        vodContents = {}
        for i in range(0,contentsNum):
            vodContent = {}
            contentId = contents[i]["id"] + "~" + contents[i]['instanceId']
            vodContent['id'] = contents[i]["id"]
            vodContent['contentId'] = contentId
            vodContent['videoFormat'] = contents[i]['videoFormat']
            if contents[i]['contentNdsDrmAttributes']['isDrmFree']:
                vodContent['drmType'] = 'none'
            else:
                vodContent['drmType'] = 'vgDrm'
            self.set_optional_value(vodContent, 'rating', contents, i, 'parentalRating', 'rating')
            if 'rating' in vodContent and vodContent['rating'] >= self.YOUTH_LIMIT_RATING:
                vodContent['isYouth'] = True
            else:
                vodContent['isYouth'] = False
            vodContent['offers'] = contents[i]['offerIdList'] if 'offerIdList' in contents[i] else contents[i]['allOfferIdList']
            vodContent['title'] = contents[i]['title'].encode('utf-8','ignore')
            vodContent['isErotic'] = contents[i]['erotic']

            vodContent['policy'] = self.isPolicyOffer(vodContent['offers'])
            vod_url = self.get_vodUri(contentId, vodContent['offers'][0])
            if vod_url is None:
                continue
            vodContent['url'] = vod_url
            self.set_optional_value(vodContent, 'isSubscription', contents, i, 'contentNdsDrmAttributes', 'isSubscription')
            self.set_optional_value(vodContent, 'isIppv', contents, i, 'contentNdsDrmAttributes', 'isIppv')
            self.set_optional_value(vodContent, 'isOppv', contents, i, 'contentNdsDrmAttributes', 'isOppv')
            self.set_optional_value(vodContent, 'classificationKeys', contents, i, 'classificationKeys')
            self.set_optional_value(vodContent, 'relatedMaterial', contents, i, 'relatedMaterial')
            self.set_optional_value(vodContent, 'provider', contents, i, 'provider')
            parsedUrl = self.parse_url(vodContent['url'])
            if 'audios' in parsedUrl and parsedUrl['audios']:
                vodContent['audioLang'] = parsedUrl['audios']
            if 'subtitles' in parsedUrl and parsedUrl['subtitles']:
                vodContent['subLang'] = parsedUrl['subtitles']
            if 'defaultLang' in parsedUrl and parsedUrl['defaultLang']:
                vodContent['defaultLang'] = parsedUrl['defaultLang']

            vodContents[contentId] = vodContent

        return vodContents

    def addHHoffers(self, offers):
        assert self.default_credentials, "No default credentials"
        hhId = self.default_credentials[0]
        offer_keys = self.getOfferKey(offers)
        for offer_key in offer_keys:
            self.addAuthorizationSubscriptionUsingBoa(hhId,"SUBSCRIPTION",offer_key,"KD-SERVICES")

    def setHHoffers(self, hhId):
        svod_offers, tvod_offers = self.getAllOffers()
        offer_keys = self.getOfferKey(svod_offers)
        for offer_key in offer_keys:
            self.addAuthorizationSubscriptionUsingBoa(hhId,"SUBSCRIPTION",offer_key,"KD-SERVICES")

    def cleanup(self):
        logging.info("Start cleanup the households which created by test")
        if self.houseHolds:
            for hhId in self.houseHolds:
                if self.isHouseHoldExist(hhId):
                    self.deleteHouseHold(hhId)


    def getContent(self, contentType, contentProperties, serviceDeliveryType=ServiceDeliveryType.ALL, index=0, high_rated_trailer=None):
        if contentType == "LINEAR":
            if serviceDeliveryType is ServiceDeliveryType.ALL: #returns both cable and abr services
                contentList = self.services
            elif serviceDeliveryType is ServiceDeliveryType.ABR:
                contentList = self.abr_services
            elif serviceDeliveryType is ServiceDeliveryType.CABLE:
                contentList = self.cable_only_services
                logging.info('Warning. The content returned is cable only services and NOT playable on abr only devices.')
            else:
                self.test.log_assert(False, 'contentType %s requested is undefined' %contentType)
        elif contentType == "VOD":
            contentList = self.vod_assets
        else:
            assert False, 'contentType %s undefined' %contentType

        requiredContents = copy.deepcopy(contentList)

        for content in contentList:
            for prop in contentProperties:
                match=False
                if (prop in contentList[content]):
                    if (contentProperties[prop] == contentList[content][prop] or contentProperties[prop]=='VALUE'):
                        match = True
                    elif type(contentProperties[prop]) is list:
                            match = True
                            for val in contentProperties[prop]:
                                if val not in contentList[content][prop]:
                                    match = False
                                    break
                    if (match==False):
                        del requiredContents[content]
                        break
                else:
                    del requiredContents[content]
                    break

        keys = requiredContents.keys()
        if index >= len(requiredContents):
            self.test.log_assert(False, 'No %s content with required properties: %s for index %d' %(contentType,contentProperties,index))
        if high_rated_trailer is None:
            return keys[index]

        return self.get_vod_with_trailer(requiredContents, self.YOUTH_LIMIT_RATING, high_rated_trailer)

    def get_vod_with_trailer(self, assets, rating, high_rated_trailer):
        catalogueId = self.getCatalogueId(self.platform)
        for key in assets.keys():
            trailerId = urllib.quote_plus(assets[key]["relatedMaterial"][0]["id"])
            cmdcContentUrl = self.cmdcUrl + 'content/' + trailerId +'/uri?catalogueId={0}&region={1}'.format(catalogueId, self.cmdcRegion)
            trailer_metadata = self.send_getRequest(cmdcContentUrl)
            if high_rated_trailer:
                if trailer_metadata["deliveries"][0]["parentalRating"]["rating"] >= rating:
                    return assets[key]["contentId"]
            else:
                if trailer_metadata["deliveries"][0]["parentalRating"]["rating"] < rating:
                    return assets[key]["contentId"]

        self.test.log_assert(False, 'No VOD with trailer was found, high rated trailer: %r' %high_rated_trailer)

    def getLinearContentABR(self, contentType):
        #return (channel id (sek), channel properties) for required contentType
        if contentType == 'clear':
            channel = self.getContent("LINEAR", {'drmType':'none'}, ServiceDeliveryType.ABR, 0)
        elif contentType == 'encrypted':
            channel = self.getContent("LINEAR", {'drmType':'vgDrm'}, ServiceDeliveryType.ABR, 0)
        elif contentType == 'policyMaxTotal':
            channel = self.getContent("LINEAR", {'providerId':'Netflix'}, ServiceDeliveryType.ABR, 0)
        elif contentType == 'HD':
            channel = self.getContent("LINEAR", {'videoFormat':'hd'}, ServiceDeliveryType.ABR, 0)
        elif contentType == 'SD':
            channel = self.getContent("LINEAR", {'videoFormat':'sd'}, ServiceDeliveryType.ABR, 0)
        elif contentType == 'HBO':
            channel = self.getContent("LINEAR", {'providerId':'HBO'}, ServiceDeliveryType.ABR, 0)
        elif contentType == 'PHX-RDK-Lab':
            channel = self.getContent("LINEAR", {'providerId':'PHX-RDK-Lab'}, ServiceDeliveryType.ABR, 0)
        elif contentType == 'DeviceType':
            channel = self.getContent("LINEAR", {'videoFormat':'sd'}, ServiceDeliveryType.ABR, 0)
        elif contentType == 'any':
            channel = self.getContent("LINEAR", {'drmType':'VALUE'}, ServiceDeliveryType.ABR, 0)
        elif contentType == 'restart':
            if self.test.vgwUtils:
                try:
                    from vgw_test_utils.headend_util import get_restart_channels
                    restart_channels = get_restart_channels()
                    channel = restart_channels[0]
                except Exception:
                    logging.exception("failed to get restart channels")
                    self.test.log_assert(False, "failed to get restart channels")
            else:
                channel = "53"
        else:
            self.test.log_assert(False, 'contentType %s undefined' %contentType)

        return self.services[channel]['serviceEquivalenceKey'], self.services[channel]

    def getVodContent(self, contentTypes, params=None):
        #return (asset id, asset properties) for required contentType
        content_properties = {}
        high_rated_trailer = None
        if VodContentType.TITLE in contentTypes:
            if (params is None) or ('title' not in params):
                self.test.log_assert('no title was given, cannot search VOD')
        else:
            if VodContentType.CLEAR in contentTypes:
                content_properties.update({'drmType': 'none'})
            if VodContentType.ENCRYPTED in contentTypes:
                content_properties.update({'drmType': 'vgDrm'})
            if VodContentType.HD in contentTypes:
                content_properties.update({'videoFormat': 'hd'})
            if VodContentType.SD in contentTypes:
                content_properties.update({'videoFormat': 'sd'})
            if VodContentType.HIGH_RATED in contentTypes:
                content_properties.update({'isYouth': True})
            if VodContentType.LOW_RATED in contentTypes:
                content_properties.update({'isYouth': False})
            if VodContentType.EROTIC in contentTypes:
                content_properties.update({'isErotic': True})
            if VodContentType.NON_EROTIC in contentTypes:
                content_properties.update({'isErotic': False})
            if VodContentType.SVOD in contentTypes:
                content_properties.update({'isSubscription': True})
            if VodContentType.TVOD in contentTypes:
                content_properties.update({'isIppv': True, 'isSubscription': False})
            if VodContentType.WITH_LOW_RATED_TRAILER in contentTypes:
                content_properties.update({'relatedMaterial':'VALUE'})
                high_rated_trailer = False
            if VodContentType.WITH_HIGH_RATED_TRAILER in contentTypes:
                content_properties.update({'relatedMaterial':'VALUE'})
                high_rated_trailer = True

        if params is not None:
            content_properties.update(params)

        asset_id = self.getContent("VOD", content_properties, index=0, high_rated_trailer=high_rated_trailer)

        return self.vod_assets[asset_id]


    def getChannel(self, channelId):
        channel = None
        for service in self.services:
            if self.services[service]['serviceEquivalenceKey'] == channelId:
                channel = self.services[service]
                break
        self.test.log_assert(channel!=None, "channel %s not in cmdc channels list" %channelId)
        return channel

    def get_total_services_num(self):
        return len(self.abr_services) + len (self.cable_only_services)

    def deleteAllDevicesFromHousehold(self,hhId):
        url = self.upmUrl + "households/" + hhId + "/devices"
        headers = {'Source-Type':'SMS','Source-ID':'123','Content-Type':'application/json','Accept':'application/json'}
        devices_info = self.test.requests.get(url, headers=headers, timeout=5).json()
        for device in devices_info:
            url = self.upmUrl + "devices/" + str(device['deviceId'])
            res = self.test.requests.delete(url,headers=headers)
            assert res.status_code == 200

    def createHouseHold(self, hhId, login, offers=None, devices = None, deviceFullType=None, drmDeviceType=None, withSTB=True, withPVR=True):
        logging.info('create new HouseHold: %s login: %s' % (hhId, login))
        if self.test.vgwUtils:
            self.test.log_assert(vgw_test_utils_installed, "Vgw Test Utils not installled")
            Settings.update_defaults(dict(household_id=hhId))
            device_id = random.randint(0x1122331111, 0x112233ffdf)
            Settings.update_defaults(dict(device_id = hex(device_id).replace('0x', '').replace('L', '')))
            reset_household_provisioning(validate_in_pps=False,target_machine = "vgw10-bcm7444Se0")
            if not withSTB:
                self.deleteAllDevicesFromHousehold(hhId=hhId)

        else:
            auxHouseholdId = 'aux_'+hhId

            hh_create_request = {
            "householdId" : hhId,
            "accountId" : login,
            "auxHouseholdId" :auxHouseholdId,
            "locale" : {
                "region": region,
                "cmdcRegion": self.cmdcRegion
            },
            "credentials" : [{
                "login" : login,
                "password" : "1234"
            }]
            }

            if(withSTB):
                headers = {'Source-Type':'STB', 'Source-ID':'123', 'Content-Type':'application/json'}
            else:
                headers = {'Source-Type':'SMS', 'Source-ID':'123', 'Content-Type':'application/json'}
            url = self.upmUrl + 'households/' + hhId
            if self.test.verbose:
                logging.info("household request: " + str(url) + " headers: " + str(headers))
            r = self.test.requests.put(url, data = json.dumps(hh_create_request), headers = headers)

            assert r.status_code == httplib.CREATED, "Failed to create houseHold:\n%s" %r.text

        self.houseHolds.append(hhId)

        if offers is not None:
            self.setHouseHoldAuthorization(hhId, offers)

        if devices is not None:
            self.addHouseHoldDevices(hhId, devices, deviceFullType, drmDeviceType, withPVR)

    def getHouseHold(self, hhId):
        url = self.upmUrl + 'households/' + hhId
        headers = {'Connection':'close', 'Accept-Encoding':'gzip,deflate', 'Source-Type':'STB', 'Source-ID':'123', 'accept':'application/json'}
        r = self.test.requests.get(url, headers=headers)
        return r

    def isHouseHoldExist(self, hhId):
        hh = self.getHouseHold(hhId)
        if hh.status_code == httplib.OK:
            return True
        elif hh.status_code == httplib.NOT_FOUND:
            return False
        logging.error("Failed to get HouseHold. status=%s" %hh.status_code)
        assert (False)

    def deleteHouseHold(self, hhId):
        url = self.upmUrl + 'households/' + hhId
        headers = {'Accept-Encoding':'gzip,deflate', 'Source-Type':'STB', 'Source-ID':'123'}
        logging.debug('delete HouseHold %s' % (hhId))
        r = self.test.requests.delete(url, headers=headers)
        assert r.status_code == httplib.OK, "Failed to delete houseHold %s\n%s" %(hhId,r.text)

    def setHouseHoldAuthorization(self, hhId, offersIds, remove=False, authorizationType='SUB'):
        offersIds = list(set(offersIds))
        if authorizationType=='SUB':
            url = self.upmUrl + 'households/' + hhId + '/authorizations/subscriptions/'
        else:
            url = self.upmUrl + 'households/' + hhId + '/authorizations/titles/'
        headers = {'Source-Type':'STB','Source-ID':'123','Content-Type':'application/json'}

        if remove:
            logging.debug('Removing offers %s to HouseHold %s' % (offersIds, hhId))
        else:
            logging.debug('Adding offers %s to HouseHold %s' % (offersIds, hhId))

        for offerId in offersIds:
            if authorizationType == 'SUB':
                urlOffer = str(offerId)
                expirationDate = (datetime.datetime.now() + datetime.timedelta(days=1)).replace(microsecond=0).isoformat()
                reqBody = {"authorizationId" : urlOffer, "authorizationType": "SUBSCRIPTION", "expirationDate" : str(expirationDate) + "Z"}
            else:
                urlOffer = str(hhId + '_'+offerId)
                expirationDate = (datetime.datetime.now() + datetime.timedelta(days=1)).replace(microsecond=0).isoformat()
                reqBody = {"authorizationId" : str(offerId), "purchaseId" : urlOffer, "authorizationType": "TVOD", "startDate": "2015-12-01T12:00:00Z", "expirationDate" : str(expirationDate) + "Z"}
            if remove == False:
                r = self.test.requests.put(url + urlOffer ,data =json.dumps(reqBody), headers=headers)
                assert r.status_code == httplib.CREATED or r.status_code == httplib.OK
            else:
                r = self.test.requests.delete(url + urlOffer ,data =json.dumps(reqBody), headers=headers)
                assert r.status_code == httplib.OK

    def addHouseHoldDevices(self, hhId, devices, deviceFullType, drmDeviceType, createPVR = False):
        url = self.upmUrl + 'households/' + hhId + '/devices/'
        headers = {'Source-Type':'EPG-SERVER','Source-ID':'123','Content-Type':'application/json'}
        logging.debug('Adding devices %s to HouseHold %s' % (devices,hhId))
        for deviceId in devices:
            extDeviceId = ''
            for i in range(0, 15):
                extDeviceId = extDeviceId + random.choice('1234567890ABCDE')
            add_device_request = {
                "externalDeviceId" : extDeviceId,
                "deviceId" : deviceId,
                "friendlyName" : "companion device",
                "userId" : "USERNAME",
                "deviceFullType": deviceFullType,
                "drmDeviceId" : deviceId + 'DRM',
                "accountId" : hhId,
                "drmDeviceType" : drmDeviceType
            }
            if createPVR:
                add_device_request["deviceCategory"] = "STB"
                add_device_request["deviceFeatures"] = [ "STB", "PVR", "GATEWAY", "RDK", "HEADED-GATEWAY", \
                                                "QAM", "IP-CLIENT", "GATEWAY-AVT-CLIENT", "VGS", "5-TUNER" ]
                add_device_request["ccPackageDeviceType"] = "G8"

            r = self.test.requests.put(url + deviceId ,data = json.dumps(add_device_request), headers=headers)
            assert (r.status_code == httplib.CREATED)

    def getServiceOffers(self, services):
        svod_offers = []
        for service in services:
            svod_offers = list(set(svod_offers)|set(services[service]['offers']))

        return svod_offers

    def getVodOffers(self, vod_assets):
        svod_offers = []
        tvod_offers = []

        for asset in vod_assets:
            if vod_assets[asset]['isSubscription']:
                svod_offers = list(set(svod_offers)|set(vod_assets[asset]['offers']))
            else:
                 tvod_offers = list(set(tvod_offers)|set(vod_assets[asset]['offers']))
        return svod_offers, tvod_offers

    def getAllOffers(self):
        svod_offers = []
        tvod_offers = []
        for service in self.services:
            svod_offers = list(set(svod_offers)|set(self.services[service]['offers']))

        if self.vod_assets:
            for asset in self.vod_assets:
                if self.vod_assets[asset]['isSubscription']:
                    svod_offers = list(set(svod_offers)|set(self.vod_assets[asset]['offers']))
                else:
                     tvod_offers = list(set(tvod_offers)|set(self.vod_assets[asset]['offers']))
        return svod_offers, tvod_offers

    def getAllOffersWithoutConcurrency(self):
        svod_offers, tvod_offers = self.getAllOffers()
        for policy in policyOffers:
            if policy in svod_offers:
                svod_offers.remove(policy)
            if policy in svod_offers:
                tvod_offers.remove(policy)
        return svod_offers, tvod_offers

    def set_households_device_quota(self, hhId, quota):
        url = self.upmUrl + 'households/' + hhId + '/deviceQuota/'
        device_quata = json.dumps({ "COMPANION":  quota })
        headers = {'Source-Type':'EPG-SERVER','Source-ID':'123','Content-Type':'application/json'}
        r = self.test.requests.put(url,data = device_quata, headers=headers)
        assert (r.status_code == httplib.CREATED or r.status_code == httplib.OK), "Failed to set deviceQuota. status=%s\n%s"%(r.status_code,r.text)

    def set_households_disk_quota(self, hhId, quota):
        url = self.upmUrl + 'households/' + hhId + '/diskQuota/'
        disk_quota = quota
        headers = {'Source-Type':'STB','Source-ID':'123','Content-Type':'text/plain', 'Data-Type': 'integer'}
        r = self.test.requests.put(url,data = disk_quota, headers=headers)
        assert (r.status_code == httplib.CREATED or r.status_code == httplib.OK), "Failed to set diskQuota. status=%s\n%s"%(r.status_code,r.text)

    def setParentalRatingThreshold(self, hhId, rating):
        url = self.upmUrl + 'households/' + hhId + '/userProfiles/' + hhId + '_0/preferences'
        headers = {'Source-Type':'SMS','Source-ID':'123', 'Accept': 'text/plain', 'Content-Type': 'text/plain'}
        logging.debug("Setting  ParentalRatingThreshold = {} to HouseHold {}".format(rating, hhId))

        r = self.test.requests.put(url, data=json.dumps({"parentalRatingThreshold":rating}), headers=headers)
        assert (r.status_code == httplib.CREATED or r.status_code == httplib.OK), "Failed to set ParentalRatingThreshold. status=%s\n%s"%(r.status_code,r.text)

    def getParentalRatingThreshold(self, hhId):
        url = self.upmUrl + 'households/' + hhId + '/userProfiles/' + hhId + '_0/preferences/parentalRatingThreshold'
        headers = {'Source-Type':'SMS','Source-ID':'123', 'Accept': 'text/plain', 'Content-Type': 'text/plain'}
        logging.debug('Getting Parental Rating of HouseHold %s' % (hhId))

        r = self.test.requests.get(url, headers=headers)
        assert (r.status_code == httplib.CREATED or r.status_code == httplib.OK), "Failed to set ParentalRatingThreshold. status=%s\n%s"%(r.status_code,r.text)
        return r.text
    
    def setYouthPin(self, hhId, youthProtectionPin):
        url = self.upmUrl + 'households/' + hhId + '/preferences/youthProtectionPin'
        headers = {'Source-Type':'SMS','Source-ID':'123', 'Content-Type': 'text/plain'}
        logging.info('Setting  youthProtectionPin = %s to HouseHold %s' % (youthProtectionPin,hhId))
        r = self.test.requests.put(url, data = youthProtectionPin, headers=headers)
        assert r.status_code == httplib.OK, "Failed to set parental rating to houseHold:\n%s" %r.text

    def getYouthpincode(self, hhId):
        url = self.upmUrl + 'households/' + hhId + '/preferences/youthProtectionPin'
        headers = {'Source-Type':'SOAPUI','Source-ID':'123','Content-Type':'application/json', 'Accept':'text/plain'}
        r = self.test.requests.get(url, headers = headers)
        assert r.status_code == httplib.OK,  "Failed to get pin code to houseHold:\n%s" %r.text
        return r._content

    def createTestHouseHold(self, withSTB=True,withPVR=True):
        #Define HH with permission to all content
        currentTime = datetime.datetime.now().isoformat().replace('-', '_').replace(':', '_').replace('.', '_')
        hhId = "HH_" + currentTime
        account_id = hhId

        if (withPVR and not self.test.vgwUtils):
            devices = [str(random.randint(100, 10000)) + currentTime]
            deviceFullType="Linux-CSG_VGS"
            drmDeviceType="DRM_SECURE_CHIP_HOMEGW"
        else:
            devices = None
            deviceFullType=None
            drmDeviceType = None
        self.createHouseHold(hhId, account_id, None, devices, deviceFullType, drmDeviceType, withSTB, withPVR)

        self.setParentalRatingPin(hhId, '0000')
        self.setTenantValue(hhId,self.test.project)
        self.setYouthPin(hhId, '1111')   #Adding YouthPin , because as of now, in CTAP, interprets parentalpin as youthpin
        self.set_households_device_quota(hhId, 10)
        if (self.test.project != 'KD'):
            preferences = self.getUserprofilePreferences(hhId)
            preferences['parentalRatingThreshold'] = DEFAULT_PARENTAL_RATING_THRESHOLD
            self.updateUserprofilePreferences(hhId, preferences)
        return hhId, account_id

    def deleteApcSessions(self,houseHold):
        apcHHUrl = self.ApcSessionsUrl + '?household=' + houseHold
        logging.info('APC URL: %s' %apcHHUrl)
        r = self.test.requests.get(apcHHUrl, data = '')
        logging.info('APC server response: %s' % r.text)

        if r.status_code == httplib.OK:
            responseDict = json.loads(r.text)
            for i in range(0,len(responseDict)):
                apcSessionUrl = self.ApcSessionsUrl + '/' + responseDict[i]['id'] + '/'
                logging.info('about to delete apc session. url: %s' %apcSessionUrl)
                r = self.test.requests.delete(apcSessionUrl)
        else:
            logging.info('Will not delete. APC get sessions response is: %s ' %r.status_code )

    def getApcSession(self,houseHold, deviceId=None):
        apcHHUrl = self.ApcSessionsUrl + '?household=' + houseHold
        logging.info('APC URL: %s' %apcHHUrl)
        r = self.test.requests.get(apcHHUrl, data = '')
        logging.info('APC server response: %s' % r.text)
        assert r.status_code == httplib.OK, 'Failed to get APC sessions for HH %s\n%s'%(houseHold, r.text)
        responseDict = json.loads(r.text)
        if deviceId is not None:
            for i in range(0,len(responseDict)):
                if responseDict[i]['device'] == deviceId:
                    return responseDict[i]
            assert False, "no apc session with device id =%s" % deviceId
        else:
            return responseDict

    def session_release(self,smSessionId):
        sessionReleaseUrl = self.PrmUrl + self.StreamingSessionPath + smSessionId
        r = self.test.requests.delete(sessionReleaseUrl)
        assert r.status_code == httplib.NO_CONTENT, 'Failed to relase sessionId %s\n%s'%(smSessionId, r.text)

    def getDeviceIdFromDeviceAndHH(self, udid, hhId):
        if self.isHouseHoldExist(hhId):
            url = self.upmUrl + 'households/' + hhId + '/devices'
            logging.info('devices for HH url is' + url)
            headers = {'Source-Type':'SOAPUI','Source-ID':'123','Content-Type':'application/json', 'Accept':'application/json'}
            r = self.test.requests.get(url, headers = headers)
            if r.status_code != httplib.OK:
                logging.info("problem in retrieving devices: " + r.text)
                return None
            responseDict = json.loads(r.text)
            #find device
            for d in responseDict:
                if 'deviceType' in d and d['deviceType'] != 'STB':
                    logging.info("current device: " + json.dumps(d))
                    #logging.info("looking for device id: " + udid + " current device: " + d)
                    #if 'drmDeviceId' in d and d['drmDeviceId'] == udid:
                    #    logging.info("found it!")
                    #how do we find our device in the HH?? for now, we have only one device in the test HH, so just return it..
                    return d['deviceId']
        return None

    def getDeviceIdFromHHByManufacturer(self, hhId, manufacturer):
        if self.isHouseHoldExist(hhId):
            url = self.upmUrl + 'households/' + hhId + '/devices'
            logging.info('devices for HH url is' + url)
            headers = {'Source-Type':'SOAPUI','Source-ID':'123','Content-Type':'application/json', 'Accept':'application/json'}
            r = self.test.requests.get(url, headers = headers)
            if r.status_code != httplib.OK:
                logging.info("problem in retrieving devices: " + r.text)
                return None
            responseDict = json.loads(r.text)
            #find device
            for d in responseDict:
                logging.info("current device: " + json.dumps(d))
                if 'deviceInfo' in d and 'manufacturer' in d['deviceInfo'] and d['deviceInfo']['manufacturer'] == manufacturer:
                    logging.info("found it:" + d['deviceId'])
                    return d['deviceId']
        return None

    def set_last_tuned_channel_for_device(self, hhId, deviceId, lastTunedChannelId):
        #get devices, for getting the UPM device id of our device
        upmDeviceId = self.getDeviceIdFromDeviceAndHH(deviceId, hhId)
        if upmDeviceId != None:
            deviceUrl = self.upmUrl+"households/"+ hhId + "/devices/" + upmDeviceId + "/preferences/lastChannel"
            logging.info("upm device id url is" + deviceUrl)
            headers = {'Source-Type':'SOAPUI','Source-ID':'123','Content-Type':'text/plain', 'Accept':'text/plain'}
            r = self.test.requests.put(deviceUrl, data = json.dumps(lastTunedChannelId), headers = headers)
            assert r.status_code == httplib.OK,  "Failed to set last channel for houseHold:\n" %r.text

    def get_last_tuned_channel_for_device(self, hhId, deviceId=None):
        #get devices, for getting the UPM device id of our device
        upmDeviceId = self.getDeviceIdFromDeviceAndHH(deviceId, hhId)
        assert upmDeviceId != None, "Failed to get upmDeviceId"

        deviceUrl = self.upmUrl+"households/"+ hhId + "/devices/" + upmDeviceId + "/preferences/lastChannel"
        logging.info("upm device id url is" + deviceUrl)
        headers = {'Source-Type':'SOAPUI','Source-ID':'123','Content-Type':'text/plain', 'Accept':'text/plain'}
        r = self.test.requests.get(deviceUrl, headers = headers)
        assert r.status_code == httplib.OK,  "Failed to get last channel for houseHold:\n" %r.text
        logging.info("last tuned channel is " + r.text)
        return r.text.encode('ascii','ignore')

    # This method helps in fetching the LCS related data
    def getAttribute(self,ve_test, config, deviceIP, attribute):
        url = 'http://' + config['he']['lcsIP']
        url = url + '/loc/ipvideo/Location?IpAddress=' + deviceIP
        response = self.test.requests.get(url)
        response_result = response.status_code == 200
        ve_test.log_assert(response_result, "LCS Response did not return 200, it returned %s" % response.status_code)
        xml_data = response.text
        root = ET.fromstring(xml_data)
        attributes = root.attrib
        ve_test.log_assert(attribute in attributes,
                           "Attribute %s is not present in response. Response: %s" % (attribute, xml_data))
        return attributes[attribute]

    def setZoneGroup(self, ve_test, config, zoneGroupName, zoneGroupProvider, zoneName, restriction_type,
                         restrictValues, isAllowed=False):
        url = 'http://' + config['he']['lcsIP']
        url = url + '/loc/zone/ZoneGroup'
        headers = {'Content-Type': 'application/xml'}
        type_check = restriction_type in ['SubNet', 'MetroCode', 'PostalCode', 'State', 'CountryCode', 'ASN', 'City']
        ve_test.log_assert(type_check, "The given restriction_type is not present. Given %s: " % type_check)

        root = ET.Element("ZoneGroup")
        root.set("xmlns", "urn:com:cisco:videoscape:conductor:loc")
        root.set("name", zoneGroupName)
        root.set("provider", zoneGroupProvider)

        classifier = ET.SubElement(root, "Classifier")
        if zoneGroupProvider == "VOD":
            classifier.set("type", "REGEX")
            classifier.text = zoneGroupProvider + ".*"
        else:
            classifier.set("type", "SIMPLE")
            classifier.text = zoneGroupProvider + "." + zoneGroupName

        zone = ET.SubElement(root, "Zone")
        zone.set("name", zoneName)

        for value in restrictValues:
            subzone = ET.SubElement(zone, restriction_type)
            subzone.text = value

        if zoneName == ZONE_BLACKLISTED:
            zone = ET.SubElement(root, "Zone")
            zone.set("name", ZONE_GEO_ALLOWED)
            subzone = ET.SubElement(zone, COUNTRY_CODE)
            subzone.text = ".*"

            zone = ET.SubElement(root, "Zone")
            zone.set("name", ZONE_ONNET_ALLOWED)
            subzone = ET.SubElement(zone, ASN)
            subzone.text = ".*"

            # Adding GEO - City Policy
            zone = ET.SubElement(root, "Zone")
            zone.set("name", ZONE_GEO_CITY_ALLOWED)
            subzone = ET.SubElement(zone, CITY)
            subzone.text = ".*"


        elif zoneName == ZONE_IN_HOME:
            # Adding ONNET Policy
            zone = ET.SubElement(root, "Zone")
            zone.set("name", ZONE_ONNET_ALLOWED)
            subzone = ET.SubElement(zone, ASN)
            subzone.text = ".*"

            # Adding GEO - Country Policy
            zone = ET.SubElement(root, "Zone")
            zone.set("name", ZONE_GEO_ALLOWED)
            subzone = ET.SubElement(zone, COUNTRY_CODE)
            subzone.text = ".*"

            # Adding GEO - City Policy
            zone = ET.SubElement(root, "Zone")
            zone.set("name", ZONE_GEO_CITY_ALLOWED)
            subzone = ET.SubElement(zone, CITY)
            subzone.text = ".*"

        elif zoneName == ZONE_ONNET_ALLOWED:
            zone = ET.SubElement(root, "Zone")
            zone.set("name", ZONE_GEO_ALLOWED)
            subzone = ET.SubElement(zone, COUNTRY_CODE)
            subzone.text = ".*"

            # Adding GEO - City Policy
            zone = ET.SubElement(root, "Zone")
            zone.set("name", ZONE_GEO_CITY_ALLOWED)
            subzone = ET.SubElement(zone, CITY)
            subzone.text = ".*"



        elif zoneName == ZONE_GEO_ALLOWED:
            zone = ET.SubElement(root, "Zone")
            zone.set("name", ZONE_ONNET_ALLOWED)
            subzone = ET.SubElement(zone, ASN)
            subzone.text = ".*"

            zone = ET.SubElement(root, "Zone")
            zone.set("name", ZONE_BLACKLISTED)
            subzone = ET.SubElement(zone, SUBNET)
            subzone.text = GEO_RESTRICTED_IP

            # Adding GEO - City Policy
            zone = ET.SubElement(root, "Zone")
            zone.set("name", ZONE_GEO_CITY_ALLOWED)
            subzone = ET.SubElement(zone, CITY)
            subzone.text = ".*"

        elif zoneName == ZONE_GEO_CITY_ALLOWED:
            zone = ET.SubElement(root, "Zone")
            zone.set("name", ZONE_GEO_ALLOWED)
            subzone = ET.SubElement(zone, COUNTRY_CODE)
            subzone.text = ".*"

            zone = ET.SubElement(root, "Zone")
            zone.set("name", ZONE_ONNET_ALLOWED)
            subzone = ET.SubElement(zone, ASN)
            subzone.text = ".*"



        elif ZONE_NETWORK_TYPE == zoneName:
            # Finding the country code
            device_ip = ve_test.device_ip
            country_code = self.getAttribute(ve_test, config, device_ip, "countryCode")
            asn = self.getAttribute(ve_test, config, device_ip, "asn")
            zone = ET.SubElement(root, "Zone")
            zone.set("name", ZONE_GEO_ALLOWED)
            subzone = ET.SubElement(zone, COUNTRY_CODE)
            subzone.text = country_code

            zone = ET.SubElement(root, "Zone")
            zone.set("name", ZONE_ONNET_ALLOWED)
            subzone = ET.SubElement(zone, ASN)
            subzone.text = asn

            # Adding GEO - City Policy
            zone = ET.SubElement(root, "Zone")
            zone.set("name", ZONE_GEO_CITY_ALLOWED)
            subzone = ET.SubElement(zone, CITY)
            subzone.text = ".*"


        bodyContent = ET.tostring(root)
        lcsResponse = self.test.requests.post(url, data=bodyContent, headers=headers)

        response_result = lcsResponse.status_code == 204
        ve_test.log_assert(response_result,"LCS Response did not return 204, it returned %s" % lcsResponse.status_code)  # This method removes (undo) the changes made in zonedata.xml in LCS

    def removeZoneGroup(self, ve_test, config, zoneGroupName, zoneGroupProvider):
        url = 'http://' + config['he']['lcsIP']
        url = url + '/loc/zone/ZoneGroup/' + zoneGroupProvider + '/' + zoneGroupName

        response = self.test.requests.delete(url)
        response_result = response.status_code == 204
        ve_test.log_assert(response_result, "LCS Response did not return 204, it returned %s" % response.status_code)

    # This method fetches LCS related data
    def getZoneAttribute(self, ve_test, config, deviceIP, attribute):
        url = 'http://' + config['he']['lcsIP']
        url = url + '/loc/ipvideo/Location?IpAddress=' + deviceIP
        response = self.test.requests.get(url)
        response_result = response.status_code == 200
        ve_test.log_assert(response_result, "LCS Response did not return 200, it returned %s" % response.status_code)
        xml_data = response.text
        root = ET.fromstring(xml_data)
        attributes = root.attrib
        ve_test.log_assert(attribute in attributes,
                           "Attribute %s is not present in response. Response: %s" % (attribute, xml_data))
        return attributes[attribute]

    def getDeviceInfofromUpm(self, hhid, device):
        url = self.upmUrl + 'households/' + hhid + '/devices/' + device + '/deviceInfo'
        headers = {'Source-Type':'SOAPUI','Source-ID':'123','Content-Type':'application/json', 'Accept':'application/json'}
        r = self.test.requests.get(url, headers = headers)
        assert r.status_code == httplib.OK, "Failed to get device details from upm"
        return r.json()

    def getDevicePreferencefromUpm(self, hhid, device):
        url = self.upmUrl + 'households/' + hhid + '/devices/' + device + '/preferences'
        headers = {'Source-Type':'SOAPUI','Source-ID':'123','Content-Type':'application/json', 'Accept':'application/json'}
        r = self.test.requests.get(url, headers = headers)
        assert r.status_code == httplib.OK, "Failed to get device details from upm"
        return r.json()

    # This method is to get DeviceSettingsDetails from UPM for the house hold associated with ve_test objects
    def getDeviceSettings(self,ve_test,hhId):
        deviceUrl = ve_test.he_utils.upmUrl+"households/"+ hhId
        headers = {'Source-Type':'SMS','Source-ID':'123','Content-Type':'application/json', 'Accept':'application/json'}
        r = self.test.requests.get(deviceUrl, headers = headers)
        ve_test.log_assert ( r.status_code == httplib.OK,  "Failed to get device list for houseHold:")
        deviceSettings = json.loads(r.content)
        return deviceSettings

    def getPSDresponse(self,config,pds_uriparam):
        url=self.pdsUrl+pds_uriparam
        r = self.test.requests.get(url);
        assert r.status_code == httplib.OK , "Failed to get the configure "+ pds_uriparam + "from PDS"
        return r.json()

    def setPSDrequest(self,config,pds_uriparam,datas):
        url=self.pdsUrl+pds_uriparam
        pdsheaders = {'Content-Type': 'application/json'}
        r=self.test.requests.put(url, data=datas,headers=pdsheaders)
        assert r.status_code == httplib.NO_CONTENT , "Failed to set the configure"+ pds_uriparam + "in PDS"

    def deleteDevicefromHousehold(self, hhId, deviceid):
        if self.isHouseHoldExist(hhId):

            url = self.boaUrlv2 + '/household/' + hhId + '/device/'+ str(deviceid)
            dheaders = {'Source-Type': 'BOA'}
            r = self.test.requests.delete(url,headers=dheaders)
            if r.status_code != httplib.OK:
                logging.info("problem in deleting devices: " + r.text)
        return r.status_code

    def deleteDevicefromHouseholdRestricted(self, hhId, deviceid):
        if self.isHouseHoldExist(hhId):
            url = self.boaUrlv2 + '/household/' + hhId + '/device/companionDevice/' + str(deviceid)
            #dheaders = {'Source-Type': 'USER-PORTAL'}
            logging.info("url is " + url)
            r = self.test.requests.delete(url)
            if r.status_code != httplib.OK:
                logging.info("problem in deleting devices: " + r.text)
        return r.status_code

    def addAuthorizationSubscriptionUsingBoa(self, hhId, authorizationType , offerKey, ProviderId):
        if self.isHouseHoldExist(hhId):
            url = self.boaUrl + '/household/' + hhId + '/authorization/subscription/offerKey'
            dheaders = {'Provider-Id': ProviderId, 'Content-Type':'text/xml'}

            root = ET.Element("boa:CreateHouseholdSubscription")

            root.set("xmlns:boa", "http://protocols.cisco.com/spvtg/boa/commonapi")
            root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")

            subscription = ET.SubElement(root, "subscription")
            OfferKey = ET.SubElement(subscription,"offerKey")
            OfferKey.text = offerKey
            authType = ET.SubElement(subscription,"authorizationType")
            authType.text = authorizationType
            bodyContent = ET.tostring(root)
            r = self.test.requests.post(url, data=bodyContent, headers=dheaders)
            if r.status_code != httplib.CREATED:
                logging.info("problem in Adding authorization subscription using Boa: " + r.text)
        return r.status_code

    def deleteAuthorizationSubscriptionUsingBoa(self, hhId,offerKey, ProviderId):
        if self.isHouseHoldExist(hhId):
            url = self.boaUrl + '/household/' + hhId + '/authorization/subscription/offerKey/'+ str(offerKey)
            dheaders = {'Provider-Id': ProviderId}
            r = self.test.requests.delete(url, headers = dheaders)
            if r.status_code != httplib.OK:
                logging.info("problem in deleting authorization subscription using Boa: " + r.text)
        return r.status_code

    def getAuthorizationSubscriptionUsingUpm(self, hhId):
        subscriptions =[]
        if self.isHouseHoldExist(hhId):
            url = self.upmUrl + 'households/' + hhId + '/authorizations/subscriptions'
            gheaders = {'Source-Type': 'SMS', 'Source-Id': '123'}
            r = self.test.requests.get(url, headers = gheaders)
            if r.status_code != httplib.OK:
                logging.info("problem in getting authorization subscription using Upm: " + r.text)
            for sub in r.json():
                if sub["authorizationType"] == "SUBSCRIPTION":
                        subscriptions.append(sub["authorizationId"])
        return subscriptions

    def deleteSubscriptionUsingUpm(self, hhId):
        if self.isHouseHoldExist(hhId):
            subscriptions = self.getAuthorizationSubscriptionUsingUpm(hhId)
            for sub in subscriptions:
                url = self.upmUrl + 'households/' + hhId + '/authorizations/subscriptions/'+ sub
                dheaders = {'Source-Type': 'SMS', 'Source-Id': '123'}
                r = self.test.requests.delete(url, headers = dheaders)
                if r.status_code != httplib.OK:
                        logging.info("problem in deleting authorization subscription using Upm: " + r.text)
        return r.status_code

    def suspendProviderServiceUsingBoa(self, hhId, ProviderId):
        if self.isHouseHoldExist(hhId):
            url = self.boaUrl + '/household/' + hhId + '/enabledServices/' + ProviderId
            r = self.test.requests.delete(url)
            if r.status_code != httplib.OK:
                logging.info("problem in suspending provider service using Boa: " + r.text)
        return r.status_code

    def resumeProviderServicesUsingBoa(self, hhId, ProviderId):
        if self.isHouseHoldExist(hhId):
            url = self.boaUrl + '/household/' + hhId + '/enabledServices/' + ProviderId
            r= self.test.requests.put(url)
            if r.status_code != httplib.OK:
                logging.info("problem in suspending provider service using Boa: " + r.text)
        return r.status_code

    def getEnabledServicesUsingBoa(self, hhId):
        if self.isHouseHoldExist(hhId):
            url = self.boaUrl + '/household/' + hhId + '/enabledServices/'
            Response = self.test.requests.get(url)
            xml_data = Response.text
            root = ET.fromstring(xml_data)
            xml = root.findall("./enabledServices/service")
            services = {}
            count =0
            for element in xml:
                services[count] = xml[count].text
                count = count + 1
            return services

    def getParentalBlockedContentLinear(self,requiredRating):
        contentLists = []
        data = self.test.ctap_data_provider.send_request("GRID", None)
        self.test.log_assert(data["count"]!=0,"unable to retrieve data of grid")
        for channel in data["channels"]:

            schedule = channel["schedule"]
            channel_id = channel ["id"]
            curr_event_pr = schedule[0]["content"]["parentalRating"]["value"]
            if int(curr_event_pr) >= int(requiredRating):
                contentLists.append(channel)
                if len(contentLists) > 5:
                    break


        self.test.log_assert(contentLists != None, "No Linear blocked channel Found)")
        return contentLists


    def getParentalBlockedContent(self,contentType = "Linear", requiredRating = 7 ):

        # Iterate Through Channels to Find the List of Contents having parental rating greater than given
        contentLists = []
        if contentType == "Linear":
            contentLists = self.getParentalBlockedContentLinear(requiredRating)

        elif contentType == "VOD" :
            for key,value  in self.vod_assets.iteritems():
                if value['rating'] >= int(requiredRating) :
                    contentLists.append(value)


        return  contentLists

    def setParentalRatingPin(self, hhId, parentalRatingPin):
        url = self.upmUrl + 'households/' + hhId + '/preferences/parentalRatingPin'
        headers = {'Source-Type':'SMS','Source-ID':'123', 'Content-Type': 'text/plain'}
        logging.info('Setting  ParentalPin = %s to HouseHold %s' % (parentalRatingPin,hhId))
        r = self.test.requests.put(url, data = parentalRatingPin, headers=headers)
        assert r.status_code == httplib.OK, "Failed to set parental rating to houseHold:\n%s" %r.text
        logging.info("Parental Rating Pin Has Been Set")

    def getUserprofilePreferences(self, hhId):
        url = self.upmUrl + 'households/' + hhId + '/userProfiles/' + hhId + '_0/preferences/'
        headers = {'Source-Type': 'SMS', 'Source-ID': '123', 'Accept': 'application/json', 'Content-Type': 'text/plain'}
        logging.debug('Getting User profile Preferences of HouseHold %s' % (hhId))

        r = self.test.requests.get(url, headers=headers)
        assert (
            r.status_code == httplib.CREATED or r.status_code == httplib.OK), "Failed to get User profile Preferences. status=%s\n%s" % (
            r.status_code, r.text)
        return r.json()

    def updateUserprofilePreferences(self, hhId, body):
        url = self.upmUrl + 'households/' + hhId + '/userProfiles/' + hhId + '_0/preferences/'
        headers = {'Source-Type': 'SMS', 'Source-ID': '123', 'Accept': 'application/json',
                   'Content-Type': 'application/json'}
        logging.debug('Setting  Userpreferences to HouseHold %s' % (hhId))

        r = self.test.requests.put(url, data=json.dumps(body), headers=headers)
        assert (
            r.status_code == httplib.CREATED or r.status_code == httplib.OK), "Failed to set UserProfile preferences status=%s\n%s" % (
            r.status_code, r.text)

    def getParentalPolicies(self, hhId):
        url = self.ctapUrl + 'r1.3.0/platform/settings/pin/parental/policies'
        ctapResponse = self.send_getRequest(url)
        data=ctapResponse['thresholdsOptions']
        return data

    def getParentalRatingPin(self, hhId):
        url = self.upmUrl + 'households/' + hhId + '/preferences/parentalRatingPin'
        headers = {'Source-Type':'SOAPUI','Source-ID':'123','Content-Type':'application/json', 'Accept':'text/plain'}
        r = self.test.requests.get(url, headers = headers)
        assert r.status_code == httplib.OK,  "Failed to get pin code to houseHold:\n%s" %r.text
        return r._content

    def setTenantValue(self, hhId, tenantValue = "kd"):
        url = self.upmUrl + 'households/' + hhId + '/tenant'
        headers = {'Source-Type':'SMS','Source-ID':'123', 'Content-Type': 'text/plain'}
        logging.info('Setting  Tenant Value = %s to HouseHold %s' % (tenantValue.lower(),hhId))
        r = self.test.requests.put(url, data = tenantValue.lower(), headers=headers)
        assert r.status_code == httplib.OK, "Failed to set parental rating to houseHold:\n%s" %r.text
        logging.info("Tenant Value Has Been Set To %s",tenantValue.lower())

    def getTenantValue(self, hhId):
        url = self.upmUrl + 'households/' + hhId + '/tenant'
        headers = {'Source-Type':'SOAPUI','Source-ID':'123','Content-Type':'application/json', 'Accept':'text/plain'}
        r = self.test.requests.get(url, headers = headers)
        assert r.status_code == httplib.OK,  "Failed to get Tenant Value of houseHold:\n%s" %r.text
        return r._content

    def getOfferDetails(self, offerId):
        url = self.cmdcUrl + 'offers/' + str(offerId)
        r = self.test.requests.get(url)
        return r.json()

    def getOfferKey(self, svod_offers):
        offer_keys =[]
        for offerId in svod_offers:
             res = self.getOfferDetails(offerId)
             self.test.log_assert(res, "Cannot find offer details for offer id: " + str(offerId))
             if self.test.verbose:
                 logging.info("RES: {0}".format(res))
             offerKey = None
             if 'offers' in res and res['offers'] != {}:
                offerKey = self.test.milestones.get_value(res, "offers", 0).get('externalKey', None)
             if offerKey:
                offer_keys.append(offerKey)
             else:
                 logging.warning("No externalKey in offer:%s", str(offerId))
        return offer_keys

    def get_current_service_event(self, start_time, end_time, service_id=None, event_count=None):
        url = self.cmdcUrl + "services/schedule/" + str(start_time) + "~" + str(end_time) + "?region=" + self.cmdcRegion
        if service_id is not None:
            url += "&serviceList=" + str(service_id)
        if event_count:
            url += "&eventCount=" + str(event_count)
        result = self.send_getRequest(url, useCache=False)
        if "contents" in result["services"][0]:
            return result
        else:
            return False
    def buy_tvod_asset_via_hep_per_household(self,hhId,offerId):
        post_url ="http://{hep_address}:{hep_port}/hep/purchaseTransaction".format(**Settings)
        logging.info("POST URL for TVOD purchase is : {0}".format(post_url))
        post_headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Source-Type": "HEP",
            "Source-Id": "HEP1"
        }
        post_data  = {
            "householdId":hhId,"purchase":[{"offer":{"offerId":str(offerId)},"metadata":{"properties":{}}}]
        }
        logging.info("POST data for TVOD purchase is : {0}".format(post_data))
        resp = self.test.requests.post(post_url, data=json.dumps(post_data), headers=post_headers)
        return resp.status_code == RES_CODE_OK

    def getIpomSettingsForSek(self,sek):
        try:
            logging.info("****IN***  get ipom settings for  SEK\n")
            logging.info("get ipom settings for SEK (%s)\n", sek)
            req_url = self.ipomUrl + "/services/policies?serviceEquivalenceKey="
            logging.info("1-get ipom settings for  SEK calling using URL (%s)\n", req_url)
            req_url = req_url + "%s" % (sek)
            logging.info("2-get ipom settings for  SEK calling using URL (%s)\n", req_url)
            r = self.test.requests.get(req_url, timeout=5.0)
            rules = r.json()
        except Exception as ex:
            logging.warning(
                "Couldn't get ipom rules for channel with SEK : %s",ex)
            rules = None

        return rules

    def find_blocked_channel(self,policy_type, return_type="logical"):
        channels = self.services
        for channel in channels:
            if "serviceEquivalenceKey" in channels[channel]:
                sek = channels[channel]["serviceEquivalenceKey"]
                channel_rules = self.getIpomSettingsForSek(sek)
            else:
                channel_rules = None

            #if trickmodes restricted for this channel return lcn
            if channel_rules:
                for policy in channel_rules:
                    if policy["policy"][policy_type] == False:
                        logging.info("found restricted %s :%s \n",policy_type,channels[channel]['logicalChannelNumber'])
                        if return_type == "logical":
                            return channels[channel]['logicalChannelNumber']
                        else:
                            return sek

        return None

#################################
## function used in KSTB profile
#################################

    def get_serviceid_by_logical_channel_number(self, serviceDeliveryType, logical_channel_number):

        cmdcServicesList = self.get_linear_services_from_cmdc(serviceDeliveryType)

        #logging.info("\n\n -----> cmdcServicesList: %s \n\n" %cmdcServicesList)

        for service in cmdcServicesList:
            #logging.info("\n -----> service: %s" % service)
            #logging.info("\n -----> cmdcServicesList[service]: %s \n" % cmdcServicesList[service])
            if 'logicalChannelNumber' in cmdcServicesList[service]:
                #logging.info("\n -----> cmdcServicesList[service]['logicalChannelNumber']: %s    logical_channel_number: %s \n" % (cmdcServicesList[service]['logicalChannelNumber'], logical_channel_number))
                if cmdcServicesList[service]['logicalChannelNumber'] == logical_channel_number:
                    return cmdcServicesList[service]['serviceEquivalenceKey']
        return False

    def get_channel_number_list_from_cmdc(self, serviceDeliveryType=ServiceDeliveryType.ALL):
        cmdcServicesList = self.get_linear_services_from_cmdc(serviceDeliveryType)
        cmdcChannelNumberList = []
        for service in cmdcServicesList:
            if 'logicalChannelNumber' in cmdcServicesList[service]:
                cmdcChannelNumberList.append(cmdcServicesList[service]['logicalChannelNumber'])
        return sorted(cmdcChannelNumberList)

    def get_events_list_from_sched(self,startTime=None, logicalChannelNumber=None, eventCount=None, endTime=None):
        
        eventList = []
        if None in (startTime, logicalChannelNumber) :
            logging.error("startTime and/or logicalChannelNumber are required")
            return eventList
        
        if eventCount == None and endTime==None:
            logging.error("Please set one or both var : eventCount,endTime")
            return eventList

        #build the request url    
        url = self.schedUrl + "1.0.0/schedule"
        url = url + "?detailLevel=standard"  + "&count=1" 
        url = url + "&region=" + self.configuration["he"]["cmdcRegion"]
        
        url = url + "&logicalChannelNumber=" + repr(logicalChannelNumber)
        url = url + "&startTime=" + repr(startTime)
        
        if eventCount != None:
            url = url + "&eventCount=" + repr(eventCount)

        if endTime != None:
            url = url + "&endTime=" + repr(endTime)
            
        # logging.info("#################### URL %s" % url)
            
        r = self.test.requests.get(url, headers=self.session_guard_header, cookies=self.r_cookie)

        r_json = json.loads(r.text)
        for r_items in r_json:
            if "channels" == r_items:
                if len(r_json["channels"]) != 0 :
                    if "assets" in  r_json["channels"][0]: #channel count is set to 1
                        for asset in r_json["channels"][0]["assets"]:
                            eventList.append(asset)
                        
                        
        return eventList

    def get_vod_adult_contents_from_cmdc(self,adult="true",erotic="true"):
        catalogueId = self.getCatalogueId(self.platform)
        cmdcContentUrl = self.cmdcUrl + 'content?filter=source~vod&catalogueId=' + catalogueId + '&filter=adult~'+adult+'&filter=erotic~'+erotic
        dictReply = self.send_getRequest(cmdcContentUrl)
        he = self.configuration['he']
        lab = str(he['lab'])
        vodContents = {}
        if not (dictReply is None):
            contents = dictReply['contents']
            contentsNum = len(contents)
            logging.info('contentsNum = %s' % contentsNum)

            assert contentsNum > 0
            for i in range(0, len(contents)):
                contentId = contents[i]["id"] + "~" + contents[i]['instanceId']
                vodContent = {}
                vodContent['contentId'] = contentId
                vodContent['id'] = contents[i]["id"]
                vodContent['title'] = contents[i]["title"]
                vodContent['instanceId'] = contents[i]["instanceId"]
                vodContent['adult'] = contents[i]['adult']
                vodContent['erotic'] = contents[i]['erotic']
                vodContent['classificationKeys'] = contents[i]['classificationKeys']
                vodContents[contentId] = vodContent

        return vodContents


    def get_ratings_scheme_from_cmdc(self):
        schemeUrl = self.cmdcUrl + 'parentalRatings?scheme=01&lang=eng'
        dictReply = self.send_getRequest(schemeUrl)
                
        if not (dictReply is None):
            return dictReply['parentalRatings']

        return []

    def get_search_keyword_result_for_vod_from_cmdc(self, keyword):
        '''
        Send a search_keyword
        :return:
        '''
        # http://cmdc:5600/cmdc/suggest/AB?count=50&searchField=keyword,title,cast&catalogueId=16897
        # &region=16384~16385&lang=eng&filter=adult~false&filter=erotic~false
        catalogueId = self.getCatalogueId(self.platform)
        search_url = self.cmdcUrl + "suggest/" + keyword + "?count=50&searchField=keyword,title,cast"
        search_url = search_url + "&catalogueId=" + catalogueId
        search_url = search_url + "&region=" + self.configuration["he"]["cmdcRegion"] + "&lang=eng&filter=adult~false&filter=erotic~false"
        #logging.info('---> search_url : %s' % search_url)
        search_url_r = self.test.requests.get(search_url)
        search_url_resp = json.loads(search_url_r.text)
        #logging.info('---> search_url_resp : %s' % search_url_resp)
        return search_url_resp

    def getHouseHoldPrentalThreshold(self):
        hh = self.getHouseHold(self.getHhId())
        return hh.json()['userProfiles'][0]['preferences']['parentalRatingThreshold']


    def getCmdcDeviceType(self, deviceId):
        url = self.upmUrl + 'devices/' + deviceId + '/cmdcDeviceType'
        headers = {'Source-Type':'SMS','Source-ID':'123', 'Accept': 'text/plain', 'Content-Type': 'text/plain'}
        r = self.test.requests.get(url, headers = headers)
        assert (r.status_code == httplib.CREATED or r.status_code == httplib.OK), "Failed to set cmdcDeviceType. status=%s\n%s"%(r.status_code,r.text)
        return r.text

    def setCmdcDeviceType(self, deviceId, data):
        url = self.upmUrl + 'devices/' + deviceId + '/cmdcDeviceType'
        headers = {'Source-Type':'SMS','Source-ID':'123', 'Accept': 'text/plain', 'Content-Type': 'text/plain'}
        r = self.test.requests.put(url, data = data, headers=headers)
        logging.debug('r.status_code = %s'%r.status_code)
        assert (r.status_code == httplib.CREATED or r.status_code == httplib.OK), "Failed to set cmdcDeviceType. status=%s\n%s"%(r.status_code,r.text)




    def get_classification_from_catId_rootclassId_typeId(self, catId, rootclassId, classifId):
        '''
        Get Classification in root classification from CatalogID, Root CatalogId and classificationType
        :param catId:
        :param rootclassId:
        :param classifId:
        :return: list of Classification
        '''
        classTree_url = self.cmdcUrl + "classification/" + rootclassId + "/classification?catalogueId=" + catId + "&lang=eng"
        #logging.info("classTreeUrl:   %s" %classTree_url)
        classTree_r = self.test.requests.get(classTree_url)
        #logging.info("classTree_r:   %s" %classTree_r.text)
        listclasstype = []
        try:
            classTree_resp = json.loads(classTree_r.text)
            #logging.info("lenght of dic : %i" % len(classTree_resp['classifications']))
            for classId in range(0,len(classTree_resp['classifications'])):
                classType = classTree_resp['classifications'][classId]['type']
                #logging.info("classType : %s" % classType)
                if classType == classifId:
                    listclasstype.append(classTree_resp['classifications'][classId]['classificationId'])
                    #logging.info("classificationId : %s" % classTree_resp['classifications'][classId]['classificationId'])
            return listclasstype
        except : return []
    
    def get_assetIds_from_classif_list(self, catId, classifList):
        '''
        Get assets list  from CatalogID and classifications list
        :param catId:
        :param classifList:
        :return: list of assets
        :return: dictionnary contentId and contentInstanceId
        '''
        dicassetsids = {}
        assetsTitleList=[]
        try:
            for classId in classifList:
                assetsList_url = self.cmdcUrl + "content?classificationId=" + classId + "&collapse=false&catalogueId=" + catId + "&region=" + self.configuration["he"]["cmdcRegion"]
                #logging.info("assetsList_url : %s" % assetsList_url)
                assetsList_r = self.test.requests.get(assetsList_url)
                #logging.info("assetsList_r.text : %s" % assetsList_r.text)
                assetsList_resp = json.loads(assetsList_r.text)
                #logging.info("lenght of dic : %i" % len(assetsList_resp['contents']))
                #logging.info("assetsList_resp = %s" % assetsList_resp)
                for assetId in range(0,len(assetsList_resp['contents'])):
                    #logging.info("AssetId : %s  AssetInstanceId : %s" % (assetsList_resp['contents'][assetId]['id'], assetsList_resp['contents'][assetId]['instanceId']))
                    dicassetsids[(assetsList_resp['contents'][assetId]['id']).replace('://','%3A%2F%2F')] = (assetsList_resp['contents'][assetId]['instanceId']).replace('://','%3A%2F%2F')
                    assetsTitleList.append(assetsList_resp['contents'][assetId]['title'])
            return dicassetsids,assetsTitleList
        except : return {},[]
    

    def setUiLanguage(self, hhId, language="eng"):
        url = self.upmUrl + 'households/' + hhId + '/userProfiles/' + hhId + '_0/preferences/uiLanguage'
        headers = {'Source-Type':'SMS','Source-ID':'123', 'Accept': 'text/plain', 'Content-Type': 'text/plain'}
        logging.info('Setting  uiLanguage = %s to HouseHold %s' % (language,hhId))
        r = self.test.requests.put(url, data = language, headers=headers)
        assert (r.status_code == httplib.CREATED or r.status_code == httplib.OK), "Failed to set uiLanguage. status=%s\n%s"%(r.status_code,r.text)
        
    def getAudioLanguage(self):
        if self.houseHolds:
            for hhId in self.houseHolds:
                if self.isHouseHoldExist(hhId):
                    url = self.upmUrl + 'households/' + hhId + '/userProfiles/' + hhId + '_0/preferences/audioLanguage'
                    headers = {'Source-Type': 'SOAPUI', 'Source-ID': '123', 'Content-Type': 'application/json',
                               'Accept': 'text/plain'}
                    r = self.test.requests.get(url, headers=headers)
                    assert r.status_code == httplib.OK
                    return r._content

    def getHhId(self):
        credentials = self.get_default_credentials()
        hhid = credentials[0]
        return hhid

    def setDeviceType(self, deviceId, data):
        url = self.upmUrl + 'devices/' + deviceId + '/deviceType'
        headers = {'Source-Type':'SMS','Source-ID':'123', 'Accept': 'text/plain', 'Content-Type': 'text/plain'}
        r = self.test.requests.put(url, data = data, headers=headers)
        logging.debug('r.status_code = %s'%r.status_code)
        assert (r.status_code == httplib.CREATED or r.status_code == httplib.OK), "Failed to set deviceType. status=%s\n%s"%(r.status_code,r.text)

    def setBuyingProtectionForOnDemand(self, hhid, data):
        #Warning: does not work as of today. You need to set the BuyingProtectionForOnDemand at household creation (see createHouseHold)
        url = self.upmUrl + 'households/' + hhid + '/preferences'
        headers = {'Source-Type':'SMS','Source-ID':'123', 'Accept': 'application/json', 'Content-Type': 'application/json'}
        data = {'buyingProtectionForOnDemand':data}
        logging.debug('Setting  buyingProtectionForOnDemand = True to HouseHold %s' %hhid)
        r = self.test.requests.put(url, data = json.dumps(data), headers=headers)
        logging.debug('r.status_code = %s'%r.status_code)
        assert (r.status_code == httplib.CREATED or r.status_code == httplib.OK), "Failed to set buying protection to houseHold. status=%s\n%s"%(r.status_code,r.text)

    def get_rootClassificationID_from_catalogId(self, catId):
        '''
        Get Root ClassificationId from CatalogId
        :param catId: CatalogId
        :return:Root ClassificationId
        '''
        self.catId = catId
        rootclassId_url = self.cmdcUrl + "classification?catalogueId="
        rootclassId_url = rootclassId_url + self.catId + "&lang=eng"
        rootclassId_r = self.test.requests.get(rootclassId_url)
        rootclassId_resp = json.loads(rootclassId_r.text)
        #logging.info('ROOT_CLASSID_RESP : %s' %rootclassId_resp)
        rootclassId = rootclassId_resp['classifications'][0]['classificationId']
        #logging.info('rootclassifId : %s', rootclassId)
        return rootclassId

    def get_classificationWithContent_from_catId_rootclassId(self, catId, rootclassId):
        '''
        Get Classification with Content in root classification from CatalogID and Root CatalogId
        :param catId:
        :param rootclassId:
        :return: list of Classification With Content
        '''
        self.catId = catId
        listclassWithContent = []
        self.rootclassId = rootclassId
        classTree_url = self.cmdcUrl + "classification/"
        classTree_url = classTree_url + self.rootclassId + "/classification?catalogueId=" + self.catId + "&lang=eng"
        # logging.info("classTreeUrl:   %s" %classTree_url)
        classTree_r = self.test.requests.get(classTree_url)
        #logging.info("classTree_r:   %s" %classTree_r.text)
        classTree_resp = json.loads(classTree_r.text)
        #logging.info('rootclassifId : %s' %rootclassId)
        #logging.info('lenght of dic : %i' %len(classTree_resp['classifications']))
        for id in range(0,len(classTree_resp['classifications'])):
            classWithContent = classTree_resp['classifications'][id]['hasContent']
            if classWithContent:
                listclassWithContent.append(classTree_resp['classifications'][id])
        return listclassWithContent

    def setParentalPin(self, hhId, parentalRatingPin):
        url = self.upmUrl + 'households/' + hhId + '/preferences/parentalRatingPin'
        headers = {'Source-Type':'SMS','Source-ID':'123', 'Content-Type': 'text/plain'}
        logging.info('Setting  parentalRatingPin = %s to HouseHold %s' % (parentalRatingPin,hhId))
        r = self.test.requests.put(url, data = parentalRatingPin, headers=headers)
        assert r.status_code == httplib.OK, "Failed to set parental rating to houseHold:\n%s" %r.text

    def getParentalpincode(self):
        if self.houseHolds:
            for hhId in self.houseHolds:
                if self.isHouseHoldExist(hhId):
                    url = self.upmUrl + 'households/' + hhId + '/preferences/parentalRatingPin'
                    headers = {'Source-Type': 'SOAPUI', 'Source-ID': '123', 'Content-Type': 'application/json', 'Accept': 'text/plain'}
                    r = self.test.requests.get(url, headers=headers)
                    assert r.status_code == httplib.OK
                    return r._content

    def enableService(self, hhId, service):
        url = self.upmUrl + 'households/' + hhId + '/enabledServices/' + service
        headers = {'Source-Type':'SMS','Source-ID':'123', 'Content-Type': 'text/plain'}
        logging.info('Enable service %s to HouseHold %s' % (service,hhId))
        r = self.test.requests.put(url, headers=headers)
        assert r.status_code == httplib.OK, "Failed to enable %s service to houseHold: %s" % (service, r.text)

    def disableService(self, hhId, service):
        url = self.upmUrl + 'households/' + hhId + '/enabledServices/' + service
        headers = {'Source-Type':'SMS','Source-ID':'123', 'Content-Type': 'text/plain'}
        logging.info('Disable service %s to HouseHold %s' % (service,hhId))
        r = self.test.requests.delete(url, headers=headers)
        assert r.status_code == httplib.OK, "Failed to disable %s service to houseHold: %s" % (service, r.text)

    def isServiceEnabled(self, hhId, service):
        url = self.upmUrl + 'households/' + hhId + '/enabledServices'
        headers = {'Source-Type':'SMS','Source-ID':'123', 'Accept': 'application/json'}
        r = self.test.requests.get(url, headers=headers)
        return r.text.find(service) > -1

    def get_short_classificationWithContent_from_catId_rootclassId(self, catId, rootclassId):
        '''
        Get Classification with Content in root classification from CatalogID and Root CatalogId
        :param catId:
        :param rootclassId:
        :return: list of ClassificationId, name in Tree
        '''
        listclassWithContent = []
        classTree_resp = self.get_classificationWithContent_from_catId_rootclassId(catId, rootclassId)
        for id in range(0,len(classTree_resp)):
            listclassWithContent.append({"classID":classTree_resp[id]['classificationId'],"title":classTree_resp[id]['name'], "leaf":classTree_resp[id]['leaf']})
        return listclassWithContent


    def get_category_title_from_class_id(self,catId, rootclassId, classId):

        title = ""
        classificationId = classId
        listclassWithContent = self.get_short_classificationWithContent_from_catId_rootclassId(catId, rootclassId)
        # logging.info('rootclassifId : %s' %rootclassId)
        for menu in listclassWithContent:
            # logging.info('classId : %s' %classId.upper())
            # logging.info('menu["classID"].upper() : %s' %menu["classID"].upper())
            if classId.upper() in menu["classID"].upper():
                title = menu["title"]
                classificationId = menu["classID"]
                break

        return title, classificationId

    def get_classification_id_from_title(self,catId, rootclassId, title):

        classId = ""
        listclassWithContent = self.get_short_classificationWithContent_from_catId_rootclassId(catId, rootclassId)

        for menu in listclassWithContent:
            if title.upper() in menu["title"].upper():
                classId = menu["classID"]
                break

        return classId

    def get_content_list_from_classificationId(self, classification_id):
        '''
        Retrive the list of asset under a classificationId
        :param classification_id
        :return:Root ClassificationId
        '''
        # http://cmdc:5600/cmdc/content?count=10
        # &pset=As_StandardC
        # &classificationId=node%3Aurn%3Aspvss%3Aih%3Akd%3Aterm%3Astore%3ATV-Mediathek%3AAnimax%3ASamuraiGirls1450263713
        # &collapse=false
        # &catalogueId=16897
        # &region=16384~16385
        # &lang=eng
        # &filter=source~vod
        assets_list = []
        catalogue_id = self.getCatalogueId(self.platform)
        assets_list_url = self.cmdcUrl + "content?count=20"
        assets_list_url = assets_list_url + "&classificationId=" + classification_id + "&collapse=false"
        assets_list_url = assets_list_url + "&catalogueId=" + catalogue_id + "&region=" + self.configuration["he"]["cmdcRegion"] + "&lang=eng" + "&filter=source~vod"

        assets_list_r = self.test.requests.get(assets_list_url, headers=self.session_guard_header, cookies=self.r_cookie)
        assets_list_resp = json.loads(assets_list_r.text)

        assets_list = assets_list_resp['contents']
        return assets_list

    def get_content_list_from_search(self, phrase, source="vod", collapse="false"):
        '''
        Return the assets list for a didicated keyword search
        :return:
        '''
        # http://cmdc:5600/cmdc/content?count=20&sort=relevancy~source:vod,pvr,ltv&pset=As_StandardC
        # &searchCriterion=title,cast~ J.J. Abrams
        # &collapse=true&catalogueId=16897&region=16384~16385&lang=eng&filter=source~vod

        assets_list = []
        catalogue_id = self.getCatalogueId(self.platform)
        assets_list_url = self.cmdcUrl + "content?count=20"
        assets_list_url = assets_list_url + "&searchCriterion=title,cast~" + str(phrase) + "&collapse="+collapse
        assets_list_url = assets_list_url + "&catalogueId=" + catalogue_id + "&region=" + self.configuration["he"]["cmdcRegion"]+ "&lang=eng" + "&filter=source~"+source
        #logging.info("---> assets_list_url: %s" % assets_list_url)
        assets_list_r = self.test.requests.get(assets_list_url, headers=self.session_guard_header, cookies=self.r_cookie)
        assets_list_resp = json.loads(assets_list_r.text)
        #logging.info("---> assets_list_resp: %s" % assets_list_resp)
        assets_list = assets_list_resp['contents']
        return assets_list



#################################################################################################
# ux_api used for retrieving the cookies. 
##################################################################################################
    def doCtapInit(self):

        if self.session_guard_header == "":
            logging.error("ctap init failed: session header is not set")
            self.cleanup()
            assert False

        url = self.ctapUrl+"init"
        #url = 'http://' + self.configuration["he"]["upmIp"] + '/ctap/init'
        # logging.info("ctap init %s"%url)
        r = self.test.requests.post(url, headers = self.session_guard_header)

        # logging.info("-------------------------------------------- ctap init %s"%r.text)

        if r.status_code != httplib.OK:
            logging.error("ctap init failed: %s" % r.text)
            self.cleanup()
            assert False
        
        self.r_cookie = r.cookies

    def updateCookies(self):
        self.doCtapInit()

############################################################################################################
#   ux_api  Hub
############################################################################################################

    def request_hub_screen(self):

        url = self.ctapUrl + "1.5.0/device_type/stb/screens/hub"

        # logging.info("url : %s" %url)
        # logging.info("headers : %s" %self.session_guard_header)

        r = self.test.requests.get(url, headers=self.session_guard_header, cookies=self.r_cookie)
        # logging.info("res : %s" %(r.text))
        return r.text

    def get_hub_menu_list(self):

        r = json.loads(self.request_hub_screen())

        for i in r:
            if i == "embedded":
                for j in r[i]:
                    if j == "menuItems":
                        for k in r[i][j]:
                            if k == "items":
                                return r[i][j][k]
        return []

    def get_preferences_menu_list(self, menu_title):

        url = self.ctapUrl + "1.5.0/device_type/stb/screens/preferencesMenu?menuTitle=" + menu_title + "&focusedType=MenuItem"
        response = self.test.requests.get(url, headers=self.session_guard_header, cookies=self.r_cookie)
        r = json.loads(response.text)

        for i in r:
            if i == "embedded":
                for j in r[i]:
                    if j == "assetMenu":
                        for k in r[i][j]:
                            if k == "items":
                                return r[i][j][k]
        return []

    def get_hub_hubondemand_list(self):
        '''
        Retrieve the assets available under HubOnDemand
        '''
        r = json.loads(self.request_hub_screen())
        for i in r:
            if i == "embedded":
                for j in r[i]:
                    if j == "hubondemand":
                        for k in r[i][j]:
                            if k == "items":
                                return r[i][j][k]
        return []

    def get_hub_horizontal_menu_list(self):
        menu_list = self.get_hub_menu_list()
        horizontal_menu_list = []
        for menu_item in menu_list:
            if "id" in menu_item:
                if menu_item["id"] == "SHOWCASE":
                    if "children" in menu_item:
                        if "items" in menu_item["children"]:
                            for item in menu_item["children"]["items"]:
                                horizontal_menu_list.append(item)

        return horizontal_menu_list


    def get_hub_menuitem_title_by_item_id(self, item_id):

        menuitem_title = ""

        menu_list = self.get_hub_menu_list()

        for menu_item in menu_list:
            if "id" in menu_item:
                if menu_item["id"] == item_id:
                        if "title" in menu_item:
                            menuitem_title = menu_item["title"]
                            break

        if len(menuitem_title) :
            return menuitem_title

        horizontal_menu_list = self.get_hub_horizontal_menu_list()

        for showcase_menu_item in horizontal_menu_list:
            if "id" in showcase_menu_item:
                if showcase_menu_item["id"] == item_id:
                    if "title" in showcase_menu_item:
                        menuitem_title = showcase_menu_item["title"]
                        break

        return menuitem_title

    def get_hub_sub_menuitem_title_by_item_href(self, href_pattern):

        menuitem_title = ""

        menu_list = self.get_hub_menu_list()

        for menu_item in menu_list:
            if "items" in menu_item :
                for sub_menu_item in menu_item["items"] :
                    if "links" in sub_menu_item :
                        if "href" in sub_menu_item["links"][0] :
                            if href_pattern in sub_menu_item["links"][0]["href"]:
                                if "title" in menu_item:
                                    menuitem_title = sub_menu_item["title"]
                                    break

        return menuitem_title

    def get_preferences_menuitem_title_by_item_href(self, href_pattern):

        menuitem_title = ""
        preferences_title = "PREFERENCES"

        menu_list = self.get_preferences_menu_list(preferences_title)

        for menu_item in menu_list:
            if "items" in menu_item:
                for item in menu_item["items"]:
                    if "links" in item:
                        if menu_item["items"][0]["links"] != []:
                            if "href" in menu_item["items"][0]["links"][0]:
                                if href_pattern in menu_item["items"][0]["links"][0]["href"]:
                                    if "title" in menu_item:
                                        menuitem_title = menu_item["title"]
                                        return menuitem_title
        return menuitem_title


    def get_action_menu_actions_list(self, action_menu_json):

        for i in action_menu_json:
            if i == "embedded":
                for j in action_menu_json[i]:
                    if j == 'actionmenu':
                        for k in action_menu_json[i][j]:
                            if k == "items":
                                return action_menu_json[i][j][k]
        return []

    def get_hub_menuitem_title_by_target(self, target):

        menuitem_title = ""

        menu_list = self.get_hub_menu_list()
        
        # logging.info(menu_list)

        for menu_item in menu_list:
            if "links" in menu_item:
                if "target" in menu_item["links"][0] :
                    if menu_item["links"][0]["target"] == target:
                        if "title" in menu_item:
                            menuitem_title = menu_item["title"]
                            break

        if len(menuitem_title) :
            return menuitem_title

        horizontal_menu_list = self.get_hub_horizontal_menu_list()

        for showcase_menu_item in horizontal_menu_list:
            if "links" in showcase_menu_item:
                if "target" in showcase_menu_item["links"][0] :
                        if showcase_menu_item["links"][0]["target"] == target:
                            if "title" in showcase_menu_item:
                                menuitem_title = showcase_menu_item["title"]
                                break
        return menuitem_title

    def get_hub_default_menu_title(self):
        '''
        Returns the title of the default menu in hub ( current spec: Live TV)
        '''
        return "LIVE TV"


    def request_filter_screen(self, crumbtrail):
        url = self.ctapUrl + "1.5.0/device_type/stb/screens/filterMenu?crumbtrail=" + crumbtrail
        # logging.info("url : %s" %url)
        r = self.test.requests.get(url, headers=self.session_guard_header, cookies=self.r_cookie)
        return r.text

    def get_filter_menu_list(self, crumbtrail):

        r = json.loads(self.request_filter_screen(crumbtrail))

        for i in r:
            if i == "embedded":
                for j in r[i]:
                    if j == "assetMenu":
                        for k in r[i][j]:
                            if k == "items":
                                return r[i][j][k]


        return []


    def get_filter_menuitem_title_by_item_id(self, crumbtrail, item_id):

        menu_list = self.get_filter_menu_list(crumbtrail)

        for i in menu_list:
            if "id" in i:
                if i["id"] == item_id:
                    if "title" in i:
                        return i["title"]

        return ""

    def get_actiomenu_by_content_id(self, content_id):
        '''
        Retrive the list of actions available for a asset
        :param content_id:
        :return: list of actions
        '''
        url = self.ctapUrl + "1.5.0/device_type/stb/screens/vodActionMenu?contentId=" + content_id + "&assetType=vod"
        #logging.info("url : %s" % url)

        r = self.test.requests.get(url, headers=self.session_guard_header, cookies=self.r_cookie)
        response = json.loads(r.text)
        #logging.info("response : %s" % response)

        return response

############################################################################################################
# ux api  Fullscreen
############################################################################################################

    def get_fullscreen_url(self):
        # launch the Hub to retrieve the current fullscreen url
        hub_response = json.loads(self.request_hub_screen())
        for i in hub_response:
            if i == "links":
                #logging.info("----> links: %s" % hub_response[i])
                for k in hub_response[i]:
                    if "event" in k:
                        if k["event"] == "pagetimeout":
                            if "href" in k:
                                return k['href']
        return ""


    def get_fullscreen_content_by_href(self, fullscreen_url):

        if not len(fullscreen_url):
            return False
        # http://localhost:8081/ctap/1.5.0/device_type/stb/screens/tv?serviceId=154&isDismiss=true
        if 'http://localhost:8081/ctap' in fullscreen_url:
            # CTAP by SGW
            new_url = fullscreen_url.replace('http://localhost:8081/ctap/', self.ctapUrl)
        else:
            return False

        url_r = self.test.requests.get(new_url, headers=self.session_guard_header, cookies=self.r_cookie)
        response = json.loads(url_r.text)
        #logging.info('action menu url_resp : %s' %response)

        return response

    def get_fullscreen_content_by_service_id(self, service_id):

        if not service_id:
            return False
        fullscreen_url = self.ctapUrl + "1.5.0/device_type/stb/screens/tv?" + "serviceId=" + str(service_id)
        # http://localhost:8081/ctap/1.5.0/device_type/stb/screens/tv?serviceId=154&isDismiss=true

        url_r = self.test.requests.get(fullscreen_url, headers=self.session_guard_header, cookies=self.r_cookie)
        response = json.loads(url_r.text)
        #logging.info('action menu url_resp : %s' %response)

        return response


    def get_fullscreen_item_by_fullscreen(self, fullscreen_resp):
        for i in fullscreen_resp:
            if i == "embedded":
                for k in fullscreen_resp[i]:
                    if k == "channelList":
                        for r in fullscreen_resp[i][k]:
                            if r == "items":
                                return fullscreen_resp[i][k][r]
        return ""
