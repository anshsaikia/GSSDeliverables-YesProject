'''
Created on Jun 28, 2015

@author: rweinste'''

''' Constants '''
FIRST_LAUNCH_TIMEOUT = 60
HE_INIT_TIMEOUT = 300
NOTIFICATION_SCREEN_NAME = "notification"

__author__ = 'bwarshaw'

from tests_framework.ve_tests.tests_conf import configuration ,set_device_type

import logging
from time import sleep, time, strptime
from enum import Enum
import sys
import os
import re
from commands import getstatusoutput
import pytest
import importlib
import json
import calendar
from requests import get
from tests_framework.ve_tests.assert_mgr import AssertMgr


class VeTestLoginType(Enum):
    login = "login"
    custom = "custom"
    none = "none"

class VeTestApi(object):

    def fix_title(self, title):
        chars_to_replace = " .:/\\\"@!#$%^&*()"
        for char in chars_to_replace:
            title = title.replace(char, '_')
        title = title[:30]
        return title

    def __init__(self, title="", useAssertMgr=False, vgwUtils = True):
        reload(sys)
        sys.setdefaultencoding("utf-8")
        #default values
        self.use_appium = None
        self.assert_error = None
        self.orig_title = title
        self.title = self.fix_title(title)
        self.login_types = VeTestLoginType
        self.login = VeTestLoginType.none
        self.stop_app = False
        self.app_launched = False
        self.ending = False
        self.start_time = None
        self.he_utils = None
        self.cmdc_queries = None
        self.ta_queries = None
        self.startup_screen = None
        self.start_test_from_screen = None
        self.supported_screens = None
        self.app_mode = None
        self.appium = None
        self.app_type = None
        self.profile = None
        self.verbose = False
        self.device_type = None
        self.sayIsActive = None
        self.stayOnAssert = None
        self.platform = None
        self.is_dummy = None
        self.is_fixed_household = None
        self.project = None
        self.webApp = None
        self.browser = None
        self.project_type = None
        self.autoPin = False
        self.waitAfterLaunch = False
        self.useUXApi = False
        #initialization
        self.useAssertMgr = useAssertMgr
        self.configuration = configuration(self)
        self.logger = self.import_test_class("tests_framework.logger.logger", "Logger")
        self.milestones = self.import_test_class("tests_framework.milestones.milestones_client", "MilestonesClient")
        self.ctap_data_provider = self.import_test_class("tests_framework.ctap_util.ctap_data_provider", "CtapDataProvider")
        self.ui = self.import_test_class("tests_framework.ve_tests.ui", "VeTestUI")
        self.performance = self.import_test_class("tests_framework.ve_tests.performance", "performance")
        self.requests = self.import_test_class("tests_framework.ve_tests.ve_requests", "VeTestRequests")
        self.mirror = self.import_test_class("tests_framework.ve_tests.mirror", "VeTestMirror")

        #Assert Mgr support
        self.useAssertMgr = useAssertMgr
        if self.useAssertMgr is True:
            self.assertmgr = AssertMgr(self)

        #Profile support
        self.profile = pytest.config.getoption("--profile")
        if not self.profile:
            self.profile = self.get_config("profile", "name", None)
        if self.profile:
            self.log_assert(self.profile in self.configuration, "Cannot find '" + self.profile + "' in configuration file")
            self.log("Using profile: '" + self.profile + "'")
        if 'he' not in self.configuration:
            self.configuration['he'] = self.get_config("he")
        #Verbose support
        self.verbose = self.get_config("general", "verbose", "False", "True")
        if self.verbose:
            self.logger.setLevel(logging.INFO)
            self.logger.setLevel(logging.WARNING, "requests")
        #Device id
        self.device_id = self.get_config("device", "deviceId", None)
        #Device ip
        self.device_ip = self.get_config("device", "ip", None)
        #Platform
        self.platform = pytest.config.getoption("--platform")
        if not self.platform:
            self.platform = self.get_config("appium", "platformName", "iOS")
        #He
        self.is_fixed_household = self.get_config("he", "fixedHousehold", "False", "True")
        self.lab = self.get_config("he", "lab", "False")
        self.is_dummy = self.lab == "dummy"
        self.is_local_ctap = self.get_config("he", "local_ctap", "False", "True")
        #Dynamic
        self.dynamic = self.get_config("general", "dynamic", "False", "True")
        self.dynamicDevice = False
        self.dynamicIp = False
        if self.dynamic:
            self.dynamicDevice = True
            self.dynamicIp = True
        if not self.device_ip:
            self.dynamicIp = True
        if not self.device_id:
            self.dynamicDevice = True
        #General
        self.screenshotDir = self.get_config("general", "screenshotDir")
        self.cacheDir = self.get_config("general", "cacheDir")
        self.project = self.get_config("general", "project", "KD").upper()
        self.webApp = self.get_config("general", "webApp")
        self.browser = self.get_config("general", "browser")
        self.manage_app = self.get_config("general", "manageApp", "True", "True")
        self.install_manage = self.get_config("general", "installManage", "True", "True")
        self.use_web_login = self.get_config("general", "useWebLogin", "True", "True")
        self.ignoreLogin = self.get_config("general", "ignoreLogin", "False", "True")
        self.dynamicDevice = self.get_config("general", "dynamicDevice", self.toBoolString(self.dynamicDevice), "True")
        self.dynamicIp = self.get_config("general", "dynamicIp", self.toBoolString(self.dynamicIp), "True")
        self.stayOnAssert = self.get_config("general", "stayOnAssert", "False", "True")
        self.sayIsActive = self.get_config("general", "sayIsActive", "False", "True")
        self.vgwUtils = vgwUtils
        if self.vgwUtils:
            self.vgwUtils = self.get_config("general", "vgwUtils", "False", "True")
        self.useAltRegion = self.get_config("general", "useAltRegion", "True" if self.project=="NET" else "False", "True")
        self.takeScreenshot = self.get_config("general", "takeSnapshot", "True")
        self.overrideArgs = self.get_config("general", "override", "True", "True")
        self.login_wait = self.get_config("general", "loginWait")
        self.shotByShot = self.get_config("general", "shotByShot", "False", "True")
        self.he_timeout = self.get_config("general", "heTimeout", HE_INIT_TIMEOUT)
        self.waitAfterLaunch = self.get_config("general", "waitAfterLaunch")
        self.vgwServerName = self.get_config("CI_VARIABLES", "vlan.name", useProfile=False)
        self.platformFolder = self.get_config("general", "platformFolder", "False", "True")
        self.useCache = self.get_config("general", "useCache", "False", "True")
        self.skipDeviceCheck = self.get_config("general", "skipDeviceCheck", "False", "True")
        self.useUXApi = self.get_config("general","useUXApi","False", "True")
        if self.vgwServerName:
            if "openstack-lwr-han" in self.vgwServerName:
                self.useAltRegion = True
        #Set project type
        if self.project != "KD":
            if "androidtv" in self.get_config("appium", "appPackage", "com.cisco.videoeverywhere3.nexplayer"):
                self.project_type = "KSTB"
                self.milestones = self.import_test_class("tests_framework.milestones.milestones_kpi_client", "MilestonesKpiClient")
            else:
                self.project_type = "K"
        else:
            self.project_type = "KD"

        if self.useAssertMgr is True:
            self.assertmgr = AssertMgr(self)

        #KD live idp
        self.liveIdp = self.get_config("general", "liveIdp", "False", "True")
        #Screens
        self.screens = self.import_test_class("tests_framework.ui_building_blocks.screens", "Screens")
        self.screen = self.import_test_class("tests_framework.ui_building_blocks.screen", "Screen")

        #Head end configuration
        if self.vgwUtils:
            self.log("Retreiving vgw utils he configuration...")
            self.is_dummy = False #Override since there is no dummy in vgw utils mode
            self.setupHeConfigurationVgwUtils()
        else:
            self.log("Retreiving standard he configuration...")
            self.setupHeConfiguration()
        self.log("Retrieved he configuration")

        #Platform specifics
        if self.platform == "Android":
            self.appium = self.import_test_class("tests_framework.appium.appium_wrapper", "AndroidWrapper")
            if self.is_dummy:
                self.android_mock_server = self.import_test_class("tests_framework.CTAP_mock.android.mock_server", "AndroidMockServer")
        elif self.platform == "iOS":
            self.appium = self.import_test_class("tests_framework.appium.appium_wrapper", "IosWrapper")
        elif self.platform == "PC":
            self.appium = self.import_test_class("tests_framework.appium.appium_wrapper", "PcWrapper")

        self.he_utils = self.import_test_class("tests_framework.he_utils.he_utils", "HeUtils")
        self.cmdc_queries = self.import_test_class("tests_framework.he_utils.cmdc_querys", "CMDC")
        self.ta_queries = self.import_test_class("tests_framework.he_utils.ta_queries", "TA")

        if not self.skipDeviceCheck:
            if self.dynamicDevice:
                #Get dynamic device id
                deviceId = self.appium.getDeviceId()
                if deviceId:
                    self.device_id = deviceId
            if self.dynamicIp:
                #Get dynamic device ip
                deviceIp = self.appium.getDeviceIp()
                if deviceIp:
                    self.device_ip = deviceIp

            self.log("device identifier: " + str(self.device_id) + " ip: " + str(self.device_ip))

        self.assets = self.import_test_class("tests_framework.ve_tests.assets", "VeTestAssets")
        self.sessionAsset = self.import_test_class("tests_framework.ve_tests.assets", "SeasonAsset")
        self.cmdc = self.import_test_class("tests_framework.he_utils.cmdc_querys", "CMDC")

        if self.use_appium:
            self.appium.start_server()

        if not self.skipDeviceCheck:
            self.appium.reset_app()

    def retrieve_he_info(self, preload=None):
        try:
            self.log(("Starting async head end setup..."))
            self.he_utils.preload = preload
            self.he_utils.thread.start()
        except Exception as e:
                self.log_assert(False, "Failed to init HeUtils(), error=%s" % e)
        self.log('waiting to be ready \n')
        self.he_utils.thread.join(self.he_timeout)
        self.log_assert(self.he_utils.heUtilsFinished, "HE Actions failed with exception: " + str(self.he_utils.exception))
        if self.useUXApi :
            self.he_utils.doCtapInit()

    def import_test_class(self, path, name):
        logging.info("Loading module: " + path + " class: " + name)
        module = importlib.import_module(path)
        myclass = getattr(module, name)
        instance = myclass(self)
        return instance

    def toBoolString(self, boolean):
        if boolean:
            return "True"
        else:
            return "False"

    def get_config(self, group, name=None, default_value=None, compare_value=None, useProfile=True):
        if name:
            name = name.rstrip()
            name = name.lstrip()
        result = None
        value = default_value
        if useProfile and self.profile:
            group = self.profile
        if group in self.configuration:
            config_group = self.configuration[group]
            if not name:
                return config_group
            if name in config_group:
                value = config_group[name]
            elif 'profile' in self.configuration and name in self.configuration["profile"]:
                value = self.configuration["profile"][name]
        if compare_value:
            result = value == compare_value
        else:
            result = value
        if self.verbose:
            self.log("config: " + group + "/" + name + "=" + str(result))
        return result

    def healthcheck(self):
        self.appium.healthcheck()

    def codecheck(self):
        self.appium.codecheck()

    def begin(self, login=VeTestLoginType.login, screen=None, autoPin=False, preload=None, skipdevice=None):

        if self.is_dummy:
            pass
        else:
            self.retrieve_he_info(preload)

        if self.skipDeviceCheck:
            self.skip("Skipping test because device check ignored")

        self.autoPin = autoPin
        self.start_test_from_screen = screen
        self.ending = False
        self.log("turning on device...")
        self.appium.turn_on_device()
        self.log("launching application..")
        self.appium.launch_app()
        self.log("application launched")

        if self.waitAfterLaunch:
            self.wait(int(self.waitAfterLaunch))

        self.device_details = self.milestones.getDeviceDetails()
        if 'startup-screen' in self.device_details:
            self.startup_screen = self.screens.getScreenByName(self.device_details['startup-screen'])
        else:
            self.startup_screen = self.screens.main_hub

        if 'supported-screens' in self.device_details:
            self.supported_screens = self.device_details['supported-screens']
            self.log("Supported screens: " + str(self.supported_screens))

        else:
            self.supported_screens = None

        if 'app-mode' in self.device_details:
            self.app_mode = self.device_details['app-mode']
            self.log("Application mode: " + self.app_mode)

        set_device_type(self)
        if skipdevice and self.device_type == skipdevice:
            self.skip("Not supported on device: %s" %self.device_type)

        logging.info('\n\n *************** START TEST: %s *************** \n', self.orig_title)

        self.start_time = time()

        if self.ignoreLogin:
            login = VeTestLoginType.none

        self.login = login

        if self.is_dummy:
            self.startup_screen.verify_active(timeout=FIRST_LAUNCH_TIMEOUT)

        login_screen = self.screens.login_screen
        self.say('performing auto sign in')
        self.wait(1)
        login_screen.auto_sign_in()

        if self.platform == "Android" and login == VeTestLoginType.login:
             if not self.is_dummy and self.app_mode != "V2":
                 self.wait(10) # wait until "new device added" msg will be dismissed'
             # this is temporary - till DRMS will be replaced in campNou
             screen = self.milestones.get_current_screen()
             logging.info(' screen= ' + screen)
             self.log_assert(screen is not "login", "failed on login")
             self.screens.notification.dismiss_notification()

             if self.start_test_from_screen == None and self.startup_screen.screen_name == "main_hub":
                 self.screens.main_hub.dismiss() # starting the tests from full screen

        self.log("Finished initialization of test")
        self.appium.notify_text(self.orig_title, duration=0)

        if self.start_test_from_screen:
            if not self.start_test_from_screen.is_supported():
                self.skip("Screen " + self.start_test_from_screen.screen_name + " is not supported")
            self.log("Starting test from screen: " + self.start_test_from_screen.screen_name)
            self.start_test_from_screen.navigate()

    def fail_login_begin(self, login=VeTestLoginType.login):
        logging.info('\n\n *************** START TEST: %s *************** \n', self.title)
        self.appium.turn_on_device()
        self.appium.reset_app()
        self.appium.launch_app()
        self.start_time = time()
        self.login = login

        login_screen = self.screens.login_screen
        credentials = login_screen.test.he_utils.get_default_credentials()

        hh_id=credentials[0]
        user_name='t'
        password='123'

        login_screen.test.configuration["he"]["generated_household"] = hh_id
        login_screen.test.configuration["he"]["generated_username"] = user_name
        login_screen.test.configuration["he"]["password"] = password
        login_screen.enter_credentials(user_name, password)

        login_screen.test.appium.take_screenshot("fail_login")
        login_screen.test.wait_for_screen_assert(20, "login", msg = "Login should have failed")

        #print device info
        device_details = self.milestones.getDeviceDetails()
        logging.info('Device Details: %s', json.dumps(device_details))


    def say(self, msg):
        if self.sayIsActive:
            logging.info('saying "%s"' % msg)
            os.system('say -v sam "%s"' % msg[:80]) #we limit the length of the spoken sentence
        else:
            logging.info(msg)

    def wait(self, seconds, log=True):
        self.log_assert(seconds >= 0, "wait time must be >= 0")
        if log:
            f_code = sys._getframe().f_back.f_code
            logging.info('Sleep for ' + str(seconds) + ' seconds from function:' + f_code.co_name + ", file: " + f_code.co_filename + ":" + str(f_code.co_firstlineno))

        if seconds >= 5 and self.app_launched == True:
            self.appium.notify_sleep(seconds)

        sleep(seconds)

    def interval(self, time_interval):
        current_time = time()
        diff = current_time - self.start_time
        if diff > time_interval:
            return
        wait_time = time_interval - diff
        sleep(wait_time)

    def skip(self, message):
        self.log("Skipping test, reason: " + message)
        self.end(endFromSkip = True)
        pytest.skip(message)

    def log_assert(self, condition, msg='assert error'):
        if self.useAssertMgr:
            f_code = sys._getframe().f_back.f_code
            self.assertmgr.addCheckPoint(self.assertmgr.current_test + " " + f_code.co_name + ", file: " + f_code.co_filename + ":" + str(f_code.co_firstlineno), 0, condition, "Internal check:" + msg)
        else :
            self.logger.log_assert(condition, msg)

    def log(self, msg):
        self.logger.log(msg)

    def close_ve_test_api(self):
        if self.stop_app:
            self.appium.stop_app(self.is_fixed_household == False)

        if self.platform == "Android":
            if self.is_dummy:
                self.android_mock_server.close_mock_server()
            elif self.he_utils:
                self.he_utils.cleanup()
        elif self.platform == "iOS":
            if self.is_dummy:
                pass
            else:
                if self.login is VeTestLoginType.login:
                        if self.is_fixed_household == False:
                            self.he_utils.cleanup()
                pass

        if not self.is_fixed_household and self.appium and self.device_id and self.stop_app:
            self.appium.reset_app()

    def end(self, endFromAssert = False, endFromSkip = False):
        # avoid from looping
        if self.ending:
            logging.warning('asserting on ending')
            return

        status = "Success"

        if endFromSkip:
            status = "Skipped"

        if endFromAssert:
            logging.error("Last milestones saved before assert: %s " % self.milestones.elements)
            self.ending = True
            if self.stayOnAssert:
                self.stop_app = False
            status = "Failed"

        if self.stop_app:
            self.appium.log_device_info()
            if endFromAssert:
                self.appium.notify_text(self.orig_title, duration=0, color="red")
                self.appium.notify_text(self.assert_error, duration=0, color="red", row=4)
                #Display notification if exists
                elements = self.milestones.getElements(update=False)
                notification = self.screens.notification.get_notification_message(elements)
                if notification:
                    self.log("notification: " + notification)
                    self.appium.notify_text("Notification: " + notification, duration=0, color="red", row=6)
            elif endFromSkip:
                self.appium.notify_text(self.orig_title, duration=0, color="yellow")
            else:
                self.appium.notify_text(self.orig_title, duration=0, color="green")
        # take screenshot
        if endFromAssert and self.appium:
            self.appium.take_screenshot("failure")
        self.wait(3)

        self.close_ve_test_api()

#       self.print_item(self.requests.list, "Server Requests")

        logging.info('\n\n *************** END TEST: %s - %s *************** \n', self.orig_title, status)

    def print_item(self, item, name=None):
        self.log(name + " = " + json.dumps(item))

    def serverUrl(self, name):
        serverName = "{" + name + "_address}"
        serverPort = "{" + name + "_port}"
        serverUrl = serverName +":" + serverPort
        try:
            url = serverUrl.format(**self.Settings)
        except Exception as e:
                self.log_assert(False, "Failed to load url from server: " + name)
        return url

    def setupHeConfigurationVgwUtils(self):
        module = __import__('vgw_test_utils.settings', fromlist=['Settings'])
        self.Settings = getattr(module, 'Settings')
        if self.verbose:
            self.log("using vgwUtil with settings %s" % str(self.Settings.items()))
        he = self.configuration['he']
        he['upmIp'] = self.serverUrl('upm')
        he['boaIp'] = self.serverUrl('boa')
        he['applicationServerIp'] = self.serverUrl('agr')
        he['smStreamingSession'] = 'http://' + self.serverUrl('sm') + "/sm/streamingSession"
        he['PrmUrl'] = self.serverUrl('sm')
        he['ipomIp'] = self.serverUrl('ipom')
        he['sched'] = self.serverUrl('sched')

        defaultUrl = he['cmdcIp'] = self.serverUrl('cmdc')

        #missing servers
        he['bsmIp'] = defaultUrl
        he['ApcSessionsUrl'] = defaultUrl 
        he['lcsIP'] = defaultUrl
        he['pdsIP']= defaultUrl
        he['subnet'] = self.Settings['subnet']
        he['csds'] = 'http://csds.' + he['subnet'] + ".phx.cisco.com:8080"

    def setupHeConfiguration(self):
        he = self.configuration['he']
        lab = self.lab
        if lab:
            self.log('lab = %s' % lab)
            if  lab.startswith("openstack"):
                self.log("openstack")
                he['upmIp'] = "im-upm-upm." + lab + ".phx.cisco.com:6040"
                he['cmdcIp'] = "cm-delivery-cmdc." + lab + ".phx.cisco.com:5600"
                he['boaIp'] = "boa-boa-rest." + lab + ".phx.cisco.com:8080"
                he['applicationServerIp'] = "ctap-cue-uxapi." + lab + ".phx.cisco.com:8000"
                he['smStreamingSession'] = "http://sm-sm-rest." + lab + ".phx.cisco.com:8080/sm/streamingSession"
                he['PrmUrl'] = "sm-sm-rest." + lab + ".phx.cisco.com:8080"
                he['bsmIp'] = "om-bsm-bsm." + lab + ".phx.cisco.com:5253"
                he['ApcSessionsUrl'] = "om-apc-apc." + lab + ".phx.cisco.com:6650"
                he['lcsIP'] = "ls-lcs." + lab + ".phx.cisco.com:8080"
                he['pdsIP'] = "om-pds-pds." + lab + ".phx.cisco.com:6660"
                he['ipomIp'] = "ipom-ipom-ipom."+ lab + ".phx.cisco.com:8080"
                he['sched'] = "http://sm-sm-rest." + lab + ".phx.cisco.com:9001"
            elif lab.endswith("ciscolabs.com"):
                self.log("ciscolabs")
                standard_url = "-" + lab + ":9834"
                he['upmIp'] = "upm" + standard_url
                he['cmdcIp'] = "cmdc" + standard_url
                he['boaIp'] = "boa" + standard_url
                he['applicationServerIp'] = "refapi" + "-" + lab + ":8001"
                he['smStreamingSession'] = "smStreamingSession" + standard_url
                he['PrmUrl'] = None
                he['bsmIp'] = "bsm" + standard_url
                he['ApcSessionsUrl'] = "apc" + standard_url
                he['lcsIP'] = "lcs" + standard_url
                he['pdsIP'] = "pds" + standard_url
                he['versionServerIp'] = "versionServerIp" + standard_url
            elif lab.endswith("cisco.com"):
                self.log("standard cisco server")
                sgw_url = 'sgw.' + lab + ':8081'
                he['upmIp'] = sgw_url
                he['cmdcIp'] = sgw_url
                he['boaIp'] = sgw_url
                he['applicationServerIp'] = sgw_url
                he['smStreamingSession'] = 'http://' + sgw_url + "/sm/streamingSession"
                he['PrmUrl'] = sgw_url
                he['bsmIp'] = sgw_url
                he['ApcSessionsUrl'] = sgw_url
                he['lcsIP'] = sgw_url
                he['pdsIP'] = sgw_url
                he['versionServerIp'] = 'sesguard.' + lab + '.phx.cisco.com:8076'
                he['sched'] = sgw_url
            else:
                self.log("standard cisco server (phx)")
                sgw_url = 'sgw.' + lab + '.phx.cisco.com:8081'
                he['upmIp'] = sgw_url
                he['cmdcIp'] = sgw_url
                he['boaIp'] = sgw_url
                he['applicationServerIp'] = sgw_url
                he['smStreamingSession'] = 'http://' + sgw_url + "/sm/streamingSession"
                he['PrmUrl'] = sgw_url
                he['bsmIp'] = sgw_url
                he['ApcSessionsUrl'] = sgw_url
                he['lcsIP'] = sgw_url
                he['pdsIP'] = sgw_url
                he['versionServerIp'] = 'sesguard.' + lab + '.phx.cisco.com:8076'
                he['ipomIp'] = sgw_url
                he['sched'] = sgw_url

    def logCurrentScreen(self):
        screen = self.milestones.get_current_screen()
        self.log("screen: " + screen)

    ###############################################################################
    #
    #           TODO : Check if we need to refactor
    #
    ###############################################################################
    def move_towards(self, direction='up', wait_few_seconds=1, longpress=False):
        '''
        move to a direction
        :param direction: direction can be 'up' 'down' 'left' 'right'
        :param wait_few_seconds: wait [wait_few_seconds] seconds after the keypress
        :return: False for invalid direction, True otherwise
        '''
        if direction == 0:
            return False
        if direction == "up":
            if longpress:
                self.key_press(keyevent="KEYCODE_DPAD_UP", wait_few_seconds=wait_few_seconds, longKeyPress=True)
            else :
                self.appium.key_event("KEYCODE_DPAD_UP")
        elif direction == "down":
            if longpress:
                self.key_press(keyevent="KEYCODE_DPAD_DOWN", wait_few_seconds=wait_few_seconds, longKeyPress=True)
            else :
                self.appium.key_event("KEYCODE_DPAD_DOWN")
        elif direction == "left":
            if longpress:
                self.key_press(keyevent="KEYCODE_DPAD_LEFT", wait_few_seconds=wait_few_seconds, longKeyPress=True)
            else :
                self.appium.key_event("KEYCODE_DPAD_LEFT")
        elif direction == "right":
            if longpress:
                self.key_press(keyevent="KEYCODE_DPAD_RIGHT", wait_few_seconds=wait_few_seconds, longKeyPress=True)
            else :
                self.appium.key_event("KEYCODE_DPAD_RIGHT")
        self.wait(wait_few_seconds)
        return True

    def validate_focused_item(self, wait_few_seconds=0.5):
        '''
        validate_focused_item
        :return:
        '''
        self.appium.key_event("KEYCODE_DPAD_CENTER")
        self.wait(wait_few_seconds)
        return True

    def go_to_previous_screen(self, wait_few_seconds=0.5):
        '''
        Go to previous screen
        :return:
        '''
        self.appium.key_event("KEYCODE_BACK")
        self.wait(wait_few_seconds)
        return True

    def key_press(self, keyevent="KEYCODE_BACK", wait_few_seconds=2, longKeyPress=False):
        '''
        press a key ...
        '''
        if longKeyPress:
            self.appium.long_key_event(keyevent)
        else:
            self.appium.key_event(keyevent)
        self.wait(wait_few_seconds)

        return True

    def repeat_key_press(self,keyevent="KEYCODE_BACK", repeate_time=2, wait_few_seconds_after_keypressed=2):
        '''
        repeat pressing a key. Uses adb,
        :param keyevent: keycode. Check android keycode in adb for more information
        :param wait_few_seconds: wait [wait_few_seconds] seconds after each keypress
        :return: True
        '''
        for _ in range(repeate_time):
            self.appium.key_event(keyevent)
            self.wait(wait_few_seconds_after_keypressed)

        return True

    def wait_for_screen(self, wait_in_seconds, screen_name, compare = "=="):
        start_time = time()
        current_time = start_time
        time_out = (current_time - start_time) >= wait_in_seconds
        print "--> Waiting for screen "+screen_name+ " : current_screen = " + self.milestones.get_current_screen()
        screen_ok = self.milestones.getElement([("screen", screen_name, compare)])
        while (not screen_ok) and (not time_out) :
            current_time = time()
            print "Waiting for screen "+screen_name+ " : current_screen = " + self.milestones.get_current_screen()
            time_out = (current_time - start_time) >= wait_in_seconds
            screen_ok = self.milestones.getElement([("screen", screen_name, compare)])
            sleep(0.5)

        if screen_ok:
            print "<-- Waiting for screen "+screen_name+ " : Yes we are"
            return True
        else:
            print "<-- Waiting for screen "+screen_name+ " : NO NO NO"
            return False

    def wait_for_screen_assert(self, wait_in_seconds, screen_name, msg='assert error', compare = "=="):
        start_time = time()
        current_time = start_time
        time_out = (current_time - start_time) >= wait_in_seconds
        screen_ok = self.milestones.getElement([("screen", screen_name, compare)])

        while (not screen_ok) and (not time_out) :
            current_time = time()
            time_out = (current_time - start_time) >= wait_in_seconds
            screen_ok = self.milestones.getElement([("screen", screen_name, compare)])
            sleep(1)

        self.logger.log_assert(screen_ok, msg+". Actual screen is "+str(self.milestones.get_current_screen()))



    def check_notification_screen(self, shown, msg_title= None ,msg_text = None, msg_code = None, msg_buttons = None, focused_action = None):
        """

        :param shown: Allow to check if the screen shall be visible or not
        :param msg_title: The expected title, only when shown is true
        :param msg_text: The expected error text, only when shown is true
        :param msg_code: The expected error code, only when shown is true
        :param msg_buttons: The expected action buttons, only when shown is true
        :return: test failed if one of the expected values is not available
        """
        elements = self.milestones.getElements()
        screen = self.milestones.get_value_by_key(elements, "screen_name")
        if shown :
            self.logger.log_assert(screen == NOTIFICATION_SCREEN_NAME, "Current screen is '" + str(screen) + "', expected '"+NOTIFICATION_SCREEN_NAME+"'")
            if msg_title is not None:
                print elements
                title = self.milestones.get_value_by_key(elements, "msg_title")
                if title:
                    self.logger.log_assert(title == msg_title,"Get error title '" + title + ", expected '" + msg_title + "'")
                else:
                    self.logger.log_assert(False,"No error title available, expected '" + msg_title + "'")
            if msg_text is not None:
                print elements
                text = self.milestones.get_value_by_key(elements, "msg_text")
                if text:
                    self.logger.log_assert(msg_text in text,"Get error message '" + text + ", expected '" + msg_text + "'")
                else:
                    self.logger.log_assert(False,"No error message available, expected '" + msg_text + "'")
            if msg_code is not None:
                error = self.milestones.get_value_by_key(elements, "msg_error")
                if error:
                    self.logger.log_assert(msg_code in error,"Get error code '" + error + ", expected '" + msg_code + "'")
                else:
                    self.logger.log_assert(False,"No error code available, expected '" + msg_code + "'")
            if msg_buttons is not None:
                # nb buttons
                nb = self.milestones.get_value_by_key(elements, "button_nb")
                self.logger.log_assert(len(msg_buttons) == nb,"Got "+str(nb)+" actions, expected "+str(len(msg_buttons)))
                for val in range(nb):
                    action = self.milestones.get_value_by_key(elements, "button_name_"+str(val))
                    self.logger.log_assert(action in msg_buttons,"The action '"+action+"' , is not in : " + str(msg_buttons))
            if focused_action is not None:
                foc_action = self.milestones.get_value_by_key(elements,"focused_action")
                self.logger.log_assert(foc_action == focused_action,"Expected focused action '"+focused_action+"', got '"+foc_action+"'")
        else:
            self.logger.log_assert(screen != NOTIFICATION_SCREEN_NAME, "A notification is shown (error : "+ str(self.milestones.get_value_by_key(elements, "msg_error"))
                                   + " : "+ str(self.milestones.get_value_by_key(elements, "msg_text")) + "), but it is not expected")


    def is_notification_error(self, msg_title= None,  msg_text = None, msg_code = None, msg_buttons = None):
        """
        Return true only if the error screen is displayed with the expected values
        :param msg_title: The expected title, only when shown is true
        :param msg_text: The expected error text, only when shown is true
        :param msg_code: The expected error code, only when shown is true
        :param msg_buttons: The expected action buttons, only when shown is true
        :return:
        """
        screen = self.milestones.get_current_screen()
        if screen != NOTIFICATION_SCREEN_NAME:
            logging.info("Current screen is '" + str(screen) + "', expected '"+NOTIFICATION_SCREEN_NAME+"'")
            return False
        elements = self.milestones.getElements()
        if msg_title is not None:
            title = self.milestones.get_value_by_key(elements, "msg_title")
            if title:
                logging.info("Error title displayed is : " + title)
                is_expected_title = title == msg_title
            else:
                is_expected_title = False
        else:
            is_expected_title = True
        if msg_text is not None:
            text = self.milestones.get_value_by_key(elements, "msg_text")
            if text:
                logging.info("Error message displayed is : " + text)
                is_expected_text = msg_text in text
            else:
                is_expected_text = False
        else:
            is_expected_text = True

        if msg_code is not None:
            error = self.milestones.get_value_by_key(elements, "msg_error")
            logging.info("Error code displayed is : " + error)
            is_expected_error = msg_code in error
        else:
            is_expected_error = True

        if msg_buttons is not None:
                # nb buttons
                is_expected_action = True
                nb = self.milestones.get_value_by_key(elements, "button_nb")
                self.logger.log_assert(len(msg_buttons) != int(nb),"Got "+nb+" actions, expected "+len(msg_buttons))
                for val in range(int(nb)):
                    action = self.milestones.get_value_by_key(elements, "button_name_"+str(val))
                    if (action not in msg_buttons):
                        is_expected_action = False
        else:
            is_expected_action = True
        return is_expected_title and is_expected_text and is_expected_error and is_expected_action

    def check_timeout(self,screen_name, timeout=15):    
        status = self.wait_for_screen(timeout + 3, screen_name, "!=" )
        if not status :
            logging.error("wait for %s to timeout (%d sec) failed" %(screen_name,timeout))
        return status

    def get_clock_time(self):
        elements = self.milestones.getElements()
        is_clock_display = self.milestones.get_element_by_key(elements, "isClockEnabled")
        if not is_clock_display:
            return False

        clock_time = self.milestones.get_element_by_key(elements, "clockTime")
        if not clock_time:
            return False

        return clock_time

    def check_clock_time_update(self, previous_clock_time):
        for i in range(0,6):           # 6x10s  max
            self.wait(10)
            new_clock_time = self.get_clock_time()
            if not new_clock_time:
                logging.info("Clock is not more displayed after 1 min")
                return False
            else:
                logging.info("%d) clock displayed: %s" %(i, new_clock_time))
                if new_clock_time != previous_clock_time:
                    logging.info("has changed !")
                    return True

        if new_clock_time == previous_clock_time:
            logging.info("Clock time is not updated after 1min")
            return False

    def getInternetTime(self):
        resp = get("http://www.google.com")
        print "Google date/time: {0}".format(resp.headers['date'])
        return int(calendar.timegm((strptime(resp.headers['date'], '%a, %d %b %Y %H:%M:%S %Z'))) * 1000)

    def wifi_disconnect(self):
        self.appium.wifi_connect(False)

    def wifi_connect(self):
        self.appium.wifi_connect(True)

    def get_channel_name_display(self, channel_info_key='focused_channel_info'):
        """
        Check if the channel name is displayed
        :param channel_info_key: milestone name
        :return: True/False and the channel name if available
        """
        logging.info("Check that the channel name is displayed for the current event")
        channel_info = self.milestones.get_value_by_key(self.milestones.getElements(),channel_info_key)
        logging.info("channel_info: %s" % channel_info)
        if not channel_info:
            logging.info("no channel_info milestone")
            return False, ""
        else:
            if 'logo' in channel_info:
                if channel_info['logo'] != "" and channel_info['logo'] != None and not channel_info['logo']:
                    logging.info("logo present")
                    return False, channel_info['logo']
            if 'name' in channel_info:
                logging.info("channel name present")
                return True, channel_info['name']
        return False, ""

    def get_channel_logo_display(self, channel_info_key='focused_channel_info'):
        """
        Check if the channel logo is displayed
        :param channel_info_key: milestone name
        :return: True/False and the channel logo urlif available
        """
        logging.info("Check that the channel logo is displayed for the current event")
        channel_info = self.milestones.get_value_by_key(self.milestones.getElements(),channel_info_key)
        logging.info("channel_info: %s" % channel_info)
        if not channel_info:
            logging.info("no channel_info milestone")
            return False, ""
        else:
            if 'logo' in channel_info:
                logging.info("logo found item")
                if channel_info['logo'] != "" and channel_info['logo'] != None and channel_info['logo'] != False:
                    logging.info("logo present")
                    return True, channel_info['logo']
        return False, ""
