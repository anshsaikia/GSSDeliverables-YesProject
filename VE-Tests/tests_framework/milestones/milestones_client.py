'''
Created on Mar 23, 2015

@author: bwarshaw
'''
from tests_framework.ve_tests.tests_conf import DeviceType
from pyjsonrpc import parse_response_json
from requests import post
from json import loads
import logging
import json
from datetime import datetime
from dateutil import tz
from dateutil import parser


''' Global Constants '''
KEY = 0
VALUE = 1
OPERATOR = 2

defaultPayloadPost = {"jsonrpc": "2.0", "method": "configureApplicationForErrorTesting", "params": ["pref_app_server_base_url","https://sgw.veop.phx.cisco.com","sessionSetup"], "id" : 1}


class MilestonesClient(object):
    def __init__(self, test):
        self.test = test
        self.configuration = test.configuration
        self.device_details = None
        self.app_config_file = None
        self.elements = []
        self.last_current_screen = None
        self.screen_trail = []

    def get_manager_port(self):
        return "5080"

    def get_manager_ip(self):
        device_path = self.test.device_ip
        device_ip = device_path.split(':')
        return device_ip[0] + ":" + self.get_manager_port()

    def post_request(self, path, method, params="null", isApp=True, maxTryCount=10):
        """

        :rtype : object
        """
        response = None
        #Try milestone request until successful or timeout
        tryIndex = 0
        payload = '{"jsonrpc": "2.0", "method": "' + method + '", "params": '+params+', "id" : 1}'
        #connect to milestones
        retry = True
        while retry:
            try:
                response = post(path, data=payload)
                response = parse_response_json(response.content)
                break
            except Exception as ex:
                logging.warning("post exception: url=%s, payload=%s, ex.msg=%s", path, payload, ex.message)
                if maxTryCount <= 0:
                    if isApp:
                        #Do not stop application since milestones is failing anyway
                        self.test.stop_app = False
                        self.test.log_assert(False, "Failed to send to '%s' milestone %s. ex = %s" %(path,method,ex))
                    else:
                        self.test.log("Failed to send to '%s' milestone %s. ex = %s" %(path,method,ex))
                    retry = False
                else:
                    maxTryCount = maxTryCount - 1
                    self.test.wait(1)
                    tryIndex = tryIndex + 1
                    logging.info("Waiting for milestone request = " + str(payload) + "..." + str(tryIndex) + " tries waited")

        #parse response
        try:
            if isApp:
                if response.result == "null":
                    return None
                response = loads(response.result)
            else:
                response = response.result
        except Exception as ex:
            logging.info("Failed to load response:")
            logging.info(response)
            pass
        return response

    def post_manager_request(self, method, params="null", maxTryCount=10):
        return self.post_request("http://"+self.get_manager_ip()+"/milestones", method, params, False, maxTryCount)

    def post_milestones_request(self, method, params="null", maxTryCount=10):
        return self.post_request("http://" + self.test.device_ip + "/milestones", method, params, True, maxTryCount)

    def getElements(self, update=True, transitionTimeout=30, getCurrentScreen=True):
        if update:
            in_transition = False
            for i in range(transitionTimeout):
                response = self.post_milestones_request("enumerateMilestones")
                if self.test.verbose:
                    logging.debug(response)
                self.test.log_assert(response, "Enumerate milestones returned None!")
                self.test.app_launched = True
                if 'elements' in response:
                    self.elements = response["elements"]
                    if self.verify_element_by_key(self.elements, "in-transition"):
                         in_transition = self.get_value_by_key(self.elements, "in-transition")
                if in_transition:
                    self.test.log("in_transition")
                    self.test.wait(1, log=False)
                else:
                    if getCurrentScreen:
                        self.get_current_screen(self.elements)
                    break
            self.test.log_assert(in_transition == False, "Application stuck in transition. \n elements =  %s" + str(self.elements))

        return self.elements

    def replace_date_names(self, date):
        date_pairs = [
            ["\u05d1\u05d9\u05e0\u05d5\u05d0\u05e8", "January"],
            ["\u05d1\u05e4\u05d1\u05e8\u05d5\u05d0\u05e8", "February"],
            ["\u05d1\u05de\u05e8\u05e5", "March"],
            ["\u05d1\u05d0\u05e4\u05e8\u05d9\u05dc", "April"],
            ["\u05d1\u05de\u05d0\u05d9", "May"],
            ["\u05d1\u05d9\u05d5\u05e0\u05d9", "June"],
            ["\u05d1\u05d9\u05d5\u05dc\u05d9", "July"],
            ["\u05d1\u05d0\u05d5\u05d2\u05d5\u05e1\u05d8", "August"],
            ["\u05d1\u05e1\u05e4\u05d8\u05de\u05d1\u05e8", "September"],
            ["\u05d1\u05d0\u05d5\u05e7\u05d8\u05d5\u05d1\u05e8", "October"],
            ["\u05d1\u05e0\u05d5\u05d1\u05de\u05d1\u05e8", "November"],
            ["\u05d1\u05d3\u05e6\u05de\u05d1\u05e8", "December"],
            ["\u05d9\u05d5\u05dd \u05d0\u05f3", "Sun"],
            ["\u05d9\u05d5\u05dd \u05d1\u05f3", "Mon"],
            ["\u05d9\u05d5\u05dd \u05d2\u05f3", "Tue"],
            ["\u05d9\u05d5\u05dd \u05d3\u05f3", "Wed"],
            ["\u05d9\u05d5\u05dd \u05d4\u05f3", "Thu"],
            ["\u05d9\u05d5\u05dd \u05d5\u05f3", "Fri"],
            ["\u05e9\u05d1\u05ea", "Sat"],
            ["\u05d9\u05e0\u05d5\u05f3", "Jan"],
            ["\u05e4\u05d1\u05e8\u05f3", "Feb"],
            ["\u05de\u05e8\u05e5", "Mar"],
            ["\u05d0\u05e4\u05e8\u05f3", "Apr"],
            ["\u05de\u05d0\u05d9", "May"],
            ["\u05d9\u05d5\u05e0\u05d9", "Jun"],
            ["\u05d9\u05d5\u05dc\u05d9", "Jul"],
            ["\u05d0\u05d5\u05d2\u05f3", "Aug"],
            ["\u05e1\u05e4\u05d8\u05f3", "Sep"],
            ["\u05d0\u05d5\u05e7\u05f3", "Oct"],
            ["\u05e0\u05d5\u05d1\u05f3", "Nov"],
            ["\u05d3\u05e6\u05de\u05f3", "Dec"],
        ]
        for date_pair in date_pairs:
            date_source = date_pair[0].decode('unicode-escape')
            date_target = date_pair[1]
            date = date.replace(date_source, date_target)
        return date

    def getLocalTime(self):
        device_details = self.test.milestones.getDeviceDetails(update=True)
        localized_date_time = device_details['localized-date-time']
        localized_date_time = localized_date_time.decode("utf-8")
        localized_date_time = self.replace_date_names(localized_date_time)
        self.test.log("localized device time: " + localized_date_time)
        localTime = parser.parse(localized_date_time)
        if self.test.platform == "Android":
            localTime = localTime.replace(tzinfo=tz.gettz(device_details['timezone']))
        self.test.log("localTime: " + str(localTime))
        return localTime

    def getDeviceDetails(self, update=False):
        if self.device_details is None or update:
            self.device_details = self.post_milestones_request("getDeviceInfo")
            logging.info(self.device_details)
        self.test.log_assert(self.device_details, "Cannot retrieve device details")

        return self.device_details

    def getWindowSize(self, elements=None):
        self.getDeviceDetails()
        width = self.device_details['screen-width']
        height = self.device_details['screen-height']
        #update window size if exists
        if not elements:
            elements = self.getElements()
        window_width = self.getUniqueElementValue('window_width', elements)
        window_height = self.getUniqueElementValue('window_height', elements)
        if window_width:
            width = window_width
        if window_height:
            height = window_height
        return int(width), int(height)

    def getConfigFile(self, update=False):
        self.app_config_file = self.post_milestones_request("getConfigFile")
        logging.info(self.app_config_file)
        self.test.log_assert(self.app_config_file, "Cannot retrieve device details")
        return self.app_config_file

    def getDeviceMemory(self):
        return self.post_milestones_request("deviceMemory")

    def getProximityInfo(self):
        return self.post_milestones_request("getProximityInfo")

    def changeSettings(self, settingNamesAndValues):
        return self.post_milestones_request("preferenceRemote", settingNamesAndValues)

    def getPlaybackStatus(self, *keys):
        status = None
        playback_status = self.post_milestones_request("getPlaybackStatus")
        if keys:
            status = self.get_value(playback_status, *keys)
        else:
            status = playback_status

        if self.test.project_type == "KSTB":
            if 'sso' in status:
                if self.test.platform == "Android":
                    status['sso']['drmType'] = status['sso']['sessionDrmType']
                    status['sso']['id'] = status['sso']["sessionId"]
                else:
                    status['sso']['sessionDrmType'] = status['sso']['drmType']
                    status['sso']['sessionId'] = status['sso']['id']
                    status['sso']['sessionPlaybackUrl'] = status['sso']['links']['playUrl']['href']

        return status

    def getPcEventsCache(self):
        return self.post_milestones_request("getPcEventsCache")

    def flushCookies(self):
        return self.post_milestones_request("flushCookies")

    def flushAppCache(self):
        return self.post_milestones_request("flushAppCache")

    def deviceLogout(self):
        return self.post_milestones_request("deviceLogout")

    def input(self, params):
        response = self.post_milestones_request("input", json.dumps(params))
        return response

    def clock(self, params):
        response = self.post_milestones_request("clock", json.dumps(params))
        return response

    def launch(self):
        return self.post_manager_request("launch")

    def launchWithProduct(self):
        self.test.log("launching with ... (if does not start check your IP !)" + self.test.project)
        return self.post_manager_request("launch", params="\"" + self.test.project + "\"")

    def get_value(self, root, *keys):
        key_path = ""
        item = root
        for key in keys:
            if isinstance(item, dict):
                key_path += "['" + str(key) + "']"
                self.test.log_assert(item and key in item, "cannot find " + key_path + " in: " + str(item) + " root: " + str(root))
            else:
                key_path += "[" + str(key) + "]"
                self.test.log_assert(item and int(key) < len(item), "cannot find " + key_path + " in: " + str(item) + " root: " + str(root))
            item = item[key]
        return item

    def get_value_by_key(self, elements, key):
        if elements == None:
            return False
        for element in elements:
            for current_key in element:
                if key == current_key:
                    return element[current_key]
        return False

    def get_value_by_key_retry(self, valueName, maxRetry=10):
        retries = 0
        value = False
        while value is False and retries < maxRetry:
            milestones = self.getElements()
            value = self.get_value_by_key(milestones,valueName)
            retries +=1
            self.test.wait(1)

        return value

    def get_element_by_key(self, elements, key):
        if elements == None:
            return False
        for element in elements:
            for current_key in element:
                if key in current_key:
                    return element
        return False

    def verify_element_by_key(self, elements, key):
        for element in elements:
            for current_key in element:
                if key in current_key:
                    return True
        return False

    def compare(self, val1, val2, operator):
        if val1 is None or val2 is None:
            return False
        if operator == "==":
            return val1 == val2
        if operator == "!=":
             return val1 != val2
        if operator == "<=":
            return val1 <= val2
        if operator == ">=":
            return val1 >= val2
        if operator == ">":
            return val1 > val2
        if operator == "<":
            return val1 < val2
        self.test.log_assert((isinstance(val1, str) or isinstance(val1, unicode)) and (isinstance(val2, str) or isinstance(val2, unicode)), "Arguments must be strings")
        if operator == "(_":
            return len(val1) > 0 and val1.lower() in val2.lower()
        if operator == "_)":
            return len(val2) > 0 and val2.lower() in val1.lower()
        if operator == "in":
            return len(val1) > 0 and val2 in val1
        if operator == "===":
            return len(val1) > 0 and val2.strip() == val1.strip()
        if operator == "==_":
            return len(val1) > 0 and val2.lower() == val1.lower()

    def getElementContains(self, elements, value, key='title_text'):
        value = value.lower().encode('utf-8', 'ignore')
        for element in elements:
            if key in element:
                element_value = element[key]
                if element_value == None:
                    if value == "":
                        return element
                    else:
                        continue
                element_value = element_value.lower().replace(u'\xa0', u' ')
                element_value = unicode(element_value)
                value = unicode(value)
                if element_value in value or value in element_value:
                    return element
        return False

    def getElementByDic(self, *dic_names):
        dic_element = None
        for dic_name in dic_names:
            dic_value = self.test.milestones.get_dic_value_by_key(dic_name,"general",True).upper()
            dic_element = self.test.milestones.getElement([("title_text", dic_value, "==")])
            if dic_element:
                break
        return dic_element

    def getElementsArrayByDic(self, element_key="title_text" , dict_names=None, extra_condition= None):
        elements = []
        for dic_name in dict_names:
            dic_value = self.test.milestones.get_dic_value_by_key(dic_name,"general",True).upper()
            condition = [(element_key, dic_value, "==")]
            if extra_condition:
                condition.append(extra_condition)
            dic_element = self.test.milestones.getElement(condition)
            if dic_element:
                elements.append(dic_element)
        return elements

    def getAnyElement(self, conditions, milestones=None):
        if isinstance(conditions, str):
            conditions = [("title_text", conditions, "==")]

        if not milestones:
            milestones = self.getElements()

        for milestone in milestones:
            found = False
            for condition in conditions:
                if condition[KEY] not in milestone:
                    continue
                elif not self.compare(milestone[condition[KEY]], condition[VALUE], condition[OPERATOR]):
                    continue
                else:
                    found = True

            if found:
                return milestone

        return None

    def getElement(self, conditions, milestones=None):
        if isinstance(conditions, str):
            conditions = [("title_text", conditions, "==")]
            
        if not milestones:
            milestones = self.getElements()

        for milestone in milestones:
            allConditionKeysFound = True
            allConditionValuesFound = True
            for condition in conditions:
                if condition[KEY] not in milestone:
                    allConditionKeysFound = False
                    break
                elif not self.compare(milestone[condition[KEY]], condition[VALUE], condition[OPERATOR]):
                    allConditionValuesFound = False
                    break
            
            if allConditionKeysFound and allConditionValuesFound:
                return milestone

        return None

    def get_elements_if_has_key(self, elements, key):
        arr = []
        for element in elements:
            if key in element.keys():
                arr.append(element)
        return arr

    def get_element_by_id(self, elements, name):
        element = self.getElement([("id", name, "==")],elements)
        return element

    def getUniqueElementValue(self, name, milestones = None):
        if not milestones:
            milestones = self.getElements()

        for milestone in milestones:
            if name in milestone:
                return milestone[name]
        return None

    def verifyElement(self, conditions, milestones=None):
        if isinstance(conditions, str):
            conditions = [("title_text", conditions, "==")]

        if not milestones:
            milestones = self.getElements()

        for milestone in milestones:
            allConditionKeysFound = True
            allConditionValuesFound = True
            for condition in conditions:
                if condition[KEY] not in milestone:
                    allConditionKeysFound = False
                    break
                elif not self.compare(milestone[condition[KEY]], condition[VALUE], condition[OPERATOR]):
                    allConditionValuesFound = False
                    break

            if allConditionKeysFound and allConditionValuesFound:
                return True

        return False

    def getElementsArray(self, conditions, milestones=None):
        elements = []
        if isinstance(conditions, str):
            conditions = [("title_text", conditions, "==")]

        if not milestones:
            milestones = self.getElements()

        for milestone in milestones:
            allConditionKeysFound = True
            allConditionValuesFound = True
            for condition in conditions:
                if condition[KEY] not in milestone:
                    allConditionKeysFound = False
                    break
                elif not self.compare(milestone[condition[KEY]], condition[VALUE], condition[OPERATOR]):
                    allConditionValuesFound = False
                    break

            if allConditionKeysFound and allConditionValuesFound:
                elements.append(milestone)
        return elements

    def fix_screen_name(self, name):
        if not name:
            if self.test.project != "KD" and self.test.app_mode == "V2":
                return "not implemented"
            else:
                return "fullscreen"
        return name

    def set_current_screen(self, name):
        if self.last_current_screen != name and self.last_current_screen:
            self.screen_trail.append(self.last_current_screen)
        self.last_current_screen = name

    def get_current_screen(self, elements=None, overrideIfNotification=True):
        if elements is None:
             elements = self.getElements(getCurrentScreen=False)

        if self.test.platform == "iOS" and overrideIfNotification and not self.test.app_mode == "V2":
             if self.getElement([("screen", "tips", "==")], elements):
                 self.test.screens.tips.dismiss(elements)
             #in iOS, when notification appears, there will be TWO screen, the active one AND the notification
             notification_view = self.getElement([("screen", "notification", "==")], elements)
             if notification_view:
                dismiss = self.getElement([("dismiss", "true", "==")], elements)
                if dismiss:
                    self.test.screens.notification.dismiss_notification(ignoreScreenQuery=True)
                    elements = self.getElements(getCurrentScreen=False)
                else:
                    self.set_current_screen("notification")
                    return "notification"

        screen = self.get_value_by_key(elements, "screen")
        screen = self.fix_screen_name(screen)
        self.set_current_screen(screen)
        return screen

    def sendCommand(self, command, param1="null", param2="null"):
        if param1=="null":
            return self.post_milestones_request("sendCommand",'["'+command+'"]')
        elif param2=="null":
            return self.post_milestones_request("sendCommand",'["'+command+'","'+param1+'"]')
        else:
            return self.post_milestones_request("sendCommand",'["'+command+'","'+param1+'","'+param2+'"]')

    def getElementInBorders(self, elements, panel, strict=False, name="event_view"):
        self.test.log_assert(panel, "No panel")
        self.test.log_assert("x_pos" in panel, "No left position in panel")
        self.test.log_assert("y_pos" in panel, "No top position in panel")
        self.test.log_assert("width" in panel, "No width in panel")
        self.test.log_assert("height" in panel, "No height in panel")
        x = panel["x_pos"]
        y = panel["y_pos"]
        width = panel["width"]
        height = panel["height"]

        result = list()
        for element in elements:
            if( ("name" in element and element["name"] == name) or ("id" in element and element["id"] == "LCN")):
                if(strict):
                    if(element["x_pos"] >= x and element["x_pos"] + element["width"] < x + width and element["y_pos"] >= y and element["y_pos"] + element["height"] < y + height):
                        result.append(element)
                else:
                    if(element["x_pos"] >= x and element["x_pos"]  < x + width and element["y_pos"] >= y and element["y_pos"] < y + height):
                        result.append(element)
        return result

    ''' get dictionary key from milstones.
       type can be general or error according to the xsl table'''
    def get_dic_value_by_key(self, key, type="general", optional=False):
        response = self.post_milestones_request("getStringByResourceId",json.dumps([type, key]))
        self.test.log_assert(response, "getStringByResourceId milestones Failed")
        dic_value = response[key]
        if not optional:
            self.test.log_assert(dic_value != "", "No dict value for type: [%s], key: [%s]" % (type,key))
        return dic_value

    def getBootComponents(self):
        return self.post_milestones_request("getBootComponents")

    def update_url(self, useCase,error_context,local_ip, original_url):
        ip = local_ip
        clientUrl = "http://" + ip+ ":8080/" + error_context

        if useCase == "sessionSetup":
            if original_url is None:
                param = '["pref_app_server_base_url","' + clientUrl + '","sessionSetup"]'
            else:
                param = '["pref_app_server_base_url", "' + original_url + '","sessionSetup"]'

        elif useCase == "keepAlive":
            param = '["pref_app_server_base_url","' + clientUrl + '","keepAlive"]'

        elif useCase == "versioncheck":
            param = '["","","versionCheck"]'

        response = self.post_milestones_request(method = "configureApplicationForErrorTesting",params=param)
