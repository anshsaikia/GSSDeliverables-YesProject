"""
Created on Mar 12, 2015

@author: bwarshaw
"""

from subprocess import Popen
from signal import SIGTERM
import threading
from time import sleep
import commands
import re

from tests_framework.ui_building_blocks.screen import ScreenActions
import os
import json
import urllib
import platform
import pytest

try:
    from os import setsid, killpg
except:
    pass

''' Global constants '''
APPIUM_INIT_TIMEOUT = 5
HOME_KEY_CODE = 3
ENTER_KEY_CODE = 66
BACKGROUND_APPS_KEY_CODE = 187
ANDROID_KEYCODE_DEL = 67


class PlatformWrapper(object):
    def __init__(self, test):
        configurations = test.configuration

        self.driver = None
        self.test = test
        self.configurations = configurations
        self.appium_server_process = None
        self.screenshot_index = 0
        if self.test.screenshotDir:
            folder_path = self.get_folder_path(self.test.shotByShot)
            self.os_cmd("rm -rf " + folder_path)
            self.os_cmd("mkdir -p " + folder_path)

    def os_cmd(self, cmd, log=True, async=False):
        response = None
        if async:
            threading.Thread(target=self.os_cmd, args=(cmd,)).start()
            return None
        if self.test.verbose and log:
            self.test.log("os_cmd call: " + cmd)
        if os.name == 'nt' or os.name == 'posix':
            "windows usage"
            pipe = os.popen(cmd + ' 2>&1', 'r')
            text = pipe.read()
            pipe.close()
            response = text
        else:
            "UNIX usage"
            response = commands.getstatusoutput(cmd)[1]
        if self.test.verbose and log and response:
            self.test.log("osd_cmd response: " + str(response))
        return response

    def get_folder_path(self, subFolder):
        path = self.test.screenshotDir
        if self.test.platformFolder:
            path += "/" + self.test.platform
        if subFolder:
            path += "/" + self.test.title
        return path

    def get_element_height(self, element):
        height = element['height']
        if ('parent-height' in element) and (element['parent-height'] > 0):
            height = element['parent-height']
        return height

    def generate_move_measurements(self, start_x, start_y, distance, direction, duration=0):
        self.test.log_assert(direction in (ScreenActions.RIGHT, ScreenActions.LEFT, ScreenActions.UP, ScreenActions.DOWN) or duration > 1 or distance > 1)

        duration = self.align_duration(duration)

        if direction == ScreenActions.RIGHT:
            start_x = start_x
            start_y = start_y
            end_x = start_x + distance
            end_y = start_y

        if direction == ScreenActions.LEFT:
            start_x = start_x
            start_y = start_y
            end_x = start_x - distance
            end_y = start_y

        if direction == ScreenActions.UP:
            start_x = start_x
            start_y = start_y
            end_x = start_x
            end_y = start_y - distance

        if direction ==ScreenActions.DOWN:
            start_x = start_x
            start_y = start_y
            end_x = start_x
            end_y = start_y + distance

        return start_x, start_y, end_x, end_y, duration

    def generate_scroll_measurements(self, element, distance, direction, duration=0):
        self.test.log_assert(isinstance(element, dict) or isinstance(element, int) or isinstance(element, basestring))
        self.test.log_assert(direction in (ScreenActions.RIGHT, ScreenActions.LEFT, ScreenActions.UP, ScreenActions.DOWN) or duration > 1 or distance > 1)

        duration = self.align_duration(duration)
        height = self.get_element_height(element)

        if direction == ScreenActions.RIGHT:
            start_x = element["x_pos"] + 1
            start_y = element["y_pos"] + (height/2)
            end_x = element["x_pos"] + 1 + distance
            end_y = element["y_pos"] + (height/2)

        if direction == ScreenActions.LEFT:
            start_x = element["x_pos"] + element["width"] - 3
            start_y = element["y_pos"] + (height/2)
            end_x = element["x_pos"] + element["width"] - distance
            end_y = element["y_pos"] + (height/2)

        if direction == ScreenActions.UP:
            start_x = element["x_pos"] + (element["width"]/2)
            start_y = element["y_pos"] + (height / 2)
            end_x = element["x_pos"] + (element["width"]/2)
            end_y = element["y_pos"] + (height / 2) - distance

        if direction ==ScreenActions.DOWN:
            start_x = element["x_pos"] + (element["width"]/2)
            start_y = element["y_pos"] + (height / 2)
            end_x = element["x_pos"] + (element["width"]/2)
            end_y = element["y_pos"] + (height / 2) + distance

        return start_x, start_y, end_x, end_y, duration

    def generate_swipe_measurements(self, element, distance, direction, duration=0):
        self.test.log_assert(isinstance(element, dict) or isinstance(element, int) or isinstance(element, basestring))
        self.test.log_assert(direction in (ScreenActions.RIGHT, ScreenActions.LEFT, ScreenActions.UP, ScreenActions.DOWN) or duration > 1 or distance > 1)

        duration = self.align_duration(duration)
        height = self.get_element_height(element)

        start_x = element["x_pos"]+(element["width"]/2)
        start_y = element["y_pos"]+(height/2)
        end_x = start_x
        end_y = start_y

        if direction is ScreenActions.RIGHT:
            end_x += distance

        if direction is ScreenActions.LEFT:
            end_x -= distance

        if direction is ScreenActions.UP:
            end_y -= distance

        if direction is ScreenActions.DOWN:
            end_y += distance

        return start_x, start_y, end_x, end_y, duration

    def generate_two_fingers_swipe_measurements(self, element, distance, direction, duration=0):
        self.test.log_assert(isinstance(element, dict) or isinstance(element, int) or isinstance(element, basestring))
        self.test.log_assert(direction in (ScreenActions.UP, ScreenActions.DOWN) or duration > 1 or distance > 1)

        duration = self.align_duration(duration)
        height = self.get_element_height(element)

        if direction == ScreenActions.UP:
            delta = element["width"]/10  #half the gap between two fingers
            x_left = element["x_pos"] + (element["width"]/2) - delta
            x_right = element["x_pos"] + (element["width"]/2) + delta
            y_low = (element["y_pos"] + height) / 2 + distance / 2
            #reference, no use: y_high = element["y_pos"] + element["height"] - distance

            f1_start_x = x_left
            f1_start_y = y_low
            f1_delta_x = 0
            f1_delta_y = -distance
            f2_start_x = x_right
            f2_start_y = y_low
            f2_delta_x = 0
            f2_delta_y = -distance

        if direction == ScreenActions.DOWN:
            delta = element["width"]/10  #half the gap between two fingers
            x_left = element["x_pos"] + (element["width"]/2) - delta
            x_right = element["x_pos"] + (element["width"]/2) + delta
            #reference, no use: y_low = element["y_pos"] + element["height"] - 1
            y_high = (element["y_pos"] + height) / 2 - distance / 2

            f1_start_x = x_left
            f1_start_y = y_high
            f1_delta_x = 0
            f1_delta_y = distance
            f2_start_x = x_right
            f2_start_y = y_high
            f2_delta_x = 0
            f2_delta_y = distance

        finger_1_swipe = [f1_start_x, f1_start_y, f1_delta_x, f1_delta_y]
        finger_2_swipe = [f2_start_x, f2_start_y, f2_delta_x, f2_delta_y]

        return finger_1_swipe, finger_2_swipe, duration

    def align_duration(self, speed):
        if speed == 0:
            default_speed = self.get_default_duration()
            return default_speed
        if speed < 0:
            scroll_speed = self.get_default_duration() * (0 - speed)
            return scroll_speed
        speed = self.get_duration_scale() * speed
        return speed

    def focus_element(self, element):
        pass

class PcWrapper(PlatformWrapper):

    def __init__(self, test):
        PlatformWrapper.__init__(self, test)

        self.test.milestones.getDeviceDetails = self.getDeviceDetails
        self.test.milestones.getElements = self.getElements
        self.test.milestones.get_value_by_key = self.get_value_by_key
        self.test.milestones.getPlaybackStatus = self.getPlaybackStatus
        self.test.milestones.get_dic_value_by_key = self.get_dic_value_by_key
        self.test.ui.top_tap = self.top_tap

    def get_dic_value_by_key(self, key, type="general", optional=False):

        dictionary_json = json.loads(self.cefDriver.execute_script("return JSON.stringify(window.milestones.languageDictionaryObject)"))
        dic_value = dictionary_json['STRINGS']['ENG'][key]

        if not optional:
            self.test.log_assert(dic_value != "", "No dict value for type: [%s], key: [%s]" % (type, key))

        return dic_value

    def top_tap(self):
        back_element = self.test.milestones.getElement([("id", "back", "==")])
        self.test.appium.tap_element(back_element)

    def getPlaybackStatus(self):
        playback_status = {}

        drmPlayerState = self.cefDriver.execute_script("return window.milestones.drmPlayerState")

        if drmPlayerState == "undefined":
            playbackState = "UNKNOWN"
        elif drmPlayerState == 0 or drmPlayerState == 4:
            playbackState = "STOPPED"
        elif drmPlayerState == 1:
            playbackState = "PAUSED"
        elif drmPlayerState == 2:
            playbackState = "PLAYING"

        drmPlayerStreamType = self.cefDriver.execute_script("return window.milestones.drmPlayerStreamType")

        if drmPlayerStreamType == 0:
            playbackType = "LINEAR"
        elif drmPlayerStreamType == 2:
            playbackType = "VOD"

        playback_status['playbackState'] = playbackState
        playback_status['playbackType'] = playbackType
        #        playback_status['playbackBufferCurrent']
        #        playback_status['currentChannelId']
        #        playback_status['sso']['sessionPlaybackUrl']
        return playback_status

    def get_value_by_key(self, elements, key):
        if elements == None:
            return False

        for element in reversed(elements):
            for current_key in element:
                if key in current_key:
                    return element[current_key]
        return False

    def findBrowserDriverPath(self, name, path):
        path = path + "VE-Tests"
        for root, dirs, files in os.walk(path):
            if name in files:
                return os.path.join(root, name)

    def getDeviceDetails(self):
        deviceDetails = {}
        deviceDetails['screen-width'] = self.browserDriver.get_window_size()['width']
        deviceDetails['screen-height'] = self.browserDriver.get_window_size()['height']
        deviceDetails['device-type'] = "PC"
        deviceDetails['app-mode'] = "V2"
        # iOS reference for getDeviceDetails - {u'app-version-code': u'1.2.0', u'server_minimum_allowed': u'(null)', u'hockey-app-identifier': u'a7c4439cc39f485784c96e3fde88e9a2', u'app-version-name': u'k1.2.0', u'supported-screens': [u'tv_filter', u'library_filter', u'store_filter', u'guide', u'action_menu', u'fullscreen', u'infolayer', u'notification', u'zap_list', u'timeline', u'settings', u'tv_search'], u'timezone': u'Asia/Jerusalem', u'device-type': u'tablet', u'network': u'{\n BSSID = "80:e0:1d:e3:dc:bf";\n SSID = blizzard;\n SSIDDATA = <626c697a 7a617264>;\n}', u'localized-date-time': u'2016-11-29 08:04:02 +0000', u'os-full-version': u'Version 10.1.1 (Build 14B150)', u'screen-width': 1024, u'os-version': u'10.1.1', u'network-wifi-ip': u'fe80::5158:7bd2:61b3:6e27', u'app-language': u'en', u'startup-screen': u'tv_filter', u'app-name': u'Happy', u'drm-device-id': u'447c8c35636ad8c1', u'os-type': u'iOS', u'app-mode': u'V2', u'screen-height': 768, u'device-model': u'iPad', u'build-date': u'Feb-21-2016', u'bundle-identifier': u'com.cisco.il.happy', u'drm-unique-device-id': u'6e7a1a7f8a9b7169e267f5dd3e6683564534c4c0', u'language': u'en-IL', u'device-name': u"Cisco's iPad", u'lab-config': u'veop', u'device-manufacturer': u'Apple', u'time': 1480406642.247307}
        return deviceDetails

    def getElements(self, update=True, transitionTimeout=30, getCurrentScreen=True):
        self.test.wait(2)
        elements = []
        browserElements = self.cefDriver.find_elements_by_xpath(".//*")
        for browserElement in browserElements:
            element = {}
            if browserElement.get_attribute('id') or browserElement.get_attribute('span'):
                if browserElement.get_attribute('data-milestonesbuttontitle'):
                    element['id'] = browserElement.get_attribute('data-milestonesbuttontitle')
                    element['title_text'] = browserElement.get_attribute('data-milestonesbuttontitle')
                element['x_pos'] = browserElement.location['x']
                element['y_pos'] = browserElement.location['y']
                element['width'] = browserElement.size['width']
                element['height'] = browserElement.size['height']
                if browserElement.get_attribute('data-milestonesscreenname'):
                    element['screen'] = browserElement.get_attribute('data-milestonesscreenname')
                if browserElement.get_attribute('data-milestonesbuttonImage'):
                    element['name'] = browserElement.get_attribute('data-milestonesbuttonImage')
    #            element['event_view'] = browserElement.get_attribute('data-milestonesscreenname')
    #            element['event_type'] = browserElement.get_attribute('data-milestonesscreenname')
    #            element['menu_item_title'] = browserElement.get_attribute('data-milestonesscreenname')
    #            element['section'] = browserElement.get_attribute('data-milestonesscreenname')
    #            element['section'] = browserElement.get_attribute('data-milestonesscreenname')
                elements.append(element)
        return elements

    def turn_on_device(self):

        from selenium.webdriver.support.ui import WebDriverWait
        from selenium import webdriver

        self.test.log_assert(self.test.browser, "Can't find the browser setting in the configuration file")
        self.installDrmaDebug()

        if self.test.browser.upper() == "FIREFOX":
            # TODO: Open broswer on full screen
            # driver.manage().window().maximize();
            self.browserDriver = webdriver.Firefox()
        elif self.test.browser.upper() == "CHROME":
            options = webdriver.ChromeOptions()
            # self.browserDriver = webdriver.Chrome(chrome_options=options)
            if platform.system() == "Windows":
                options.add_argument("--start-maximized")
                self.browserDriver = webdriver.Chrome(
                    self.findBrowserDriverPath("chromedriver_WIN_2.25.exe", os.getcwd().split("VE-Tests")[0]),
                    chrome_options=options)
                cefChromeDriver = "chromedriver_WIN_2.14.exe"
            elif platform.system() == "Darwin":
                options.add_argument("--kiosk")
                # self.browserDriver = webdriver.Chrome(self.findBrowserDriverPath("chromedriver_MAC","/Users/"))
                self.browserDriver = webdriver.Chrome(
                    self.findBrowserDriverPath("chromedriver_MAC_2.25", os.getcwd().split("VE-Tests")[0]),
                    chrome_options=options)
                cefChromeDriver = "chromedriver_MAC_2.14"
        elif self.test.browser.upper() == "SAFARI":
            # TODO: Check if selenium supports this broswer and if so open broswer on full screen
            pass
        elif self.test.browser.upper() == "IE":
            # TODO: Open broswer on full screen
            self.browserDriver = webdriver.IE()

        self.test.log_assert(self.test.webApp, "Can't find the webApp setting in the configuration file")
        self.browserDriver.get(self.test.webApp)

        optionsCef = webdriver.ChromeOptions()
        optionsCef.debugger_address = "127.0.0.1:14985"
        self.cefDriver = webdriver.Chrome(self.findBrowserDriverPath(cefChromeDriver, os.getcwd().split("VE-Tests")[0]), chrome_options=optionsCef)

        self.wait_for_event("EC.presence_of_element_located((By.XPATH,"+'"//*[@id='+"'brandingLogo']"+'"))',
                            'The web app is loaded and ready to test!',
                            'The web app did not load for unexpected reason :(!')

    def installDrmaDebug(self):

        # TODO: Get the DRMA version from the web server - Omer will supply an API
        # drmaVersion2Install = os.system("curl -k -s --insecure https://web_ui-web_ui."+Settings['subnet']+":4443/vgdrm/drma_version.json | grep version")
        # drmaVersion2Install = drmaVersion2Install["version"]
        drmaVersion2Install = "7.2.55453"

        cwd = os.getcwd()
        link = "http://engci-maven-master.cisco.com/artifactory/spvss-cloud-ci-yum-dev/drma_wrapper/"

        if platform.system() == "Windows":
            fileName = "\CiscoVideoGuard_debug_WIN.exe"
            installScript = cwd.split("VE-Tests")[0] + "VE-Tests\ec_utils\PC\silent_install.bat "
        elif platform.system() == "Darwin":
            fileName = "/CiscoVideoGuard_debug_MAC.dmg"
            installScript = "~/VE-Tests/ec_utils/PC/silent_install.sh "

        site = urllib.urlopen(link + drmaVersion2Install + fileName)
        meta = site.info()
        sizeBeforeDownload = meta.getheaders("Content-Length")[0]

        urllib.urlretrieve(link + drmaVersion2Install + fileName, cwd + fileName)

        fileDownlaodedData = os.stat(cwd + fileName)
        sizeAfterDownload = fileDownlaodedData.st_size
        self.test.log_assert(sizeBeforeDownload != sizeAfterDownload,
                             "Size before download: " + str(sizeBeforeDownload) +
                             " Size after download: " + str(sizeAfterDownload))
        os.system("chmod a+x " + installScript)
        os.system(installScript + cwd + fileName)

    def uninstallDrmaDebug(self):

        cwd = os.getcwd()

        if platform.system() == "Windows":
            fileName = "\CiscoVideoGuard_debug_WIN.exe"
            installScript = cwd.split("VE-Tests")[0] + "VE-Tests\ec_utils\PC\silent_install.bat "
            os.system(installScript + cwd + fileName + " /x")
        elif platform.system() == "Darwin":
            excuteFileName = "uninstall.command"
            uninstallDrmaDebugPath = self.findDRMAPath(excuteFileName, os.getcwd().split("VE-Tests")[0])
            os.system(uninstallDrmaDebugPath)

    def findDRMAPath(self, name, path):
        for root, dirs, files in os.walk(path):
            if name in files:
                return os.path.join(root, name)

    def wait_for_event(self, condition, successMessage, failureMessage, timeOut=10):
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.common.exceptions import TimeoutException
        from selenium.webdriver.common.by import By

        try:
            WebDriverWait(self.cefDriver, timeOut).until(eval(condition))
            self.test.log(successMessage)
            return True
        except TimeoutException:
            self.test.log_assert(failureMessage)

    def send_app_to_background(self):
        self.test.milestones.input({"action": "pause-app"})
        self.test.wait(0.5)

    def send_app_to_foreground(self):
        self.manager.launch()
        self.test.wait(0.5)

    def reset_app(self):
        pass

    def stop_app(self, logout=True):

        # TODO: check and dismiss pop ups
        self.cefDriver.quit()
        self.uninstallDrmaDebug()

        cwd = os.getcwd()

        if platform.system() == "Windows":
            fileName = "/CiscoVideoGuard_debug_WIN.exe"
        elif platform.system() == "Darwin":
            fileName = "/CiscoVideoGuard_debug_MAC.dmg"
        os.remove(cwd + fileName)

    def restart_app(self):

        from selenium.webdriver.support.ui import WebDriverWait
        from selenium import webdriver

        self.browserDriver.refresh()

        if self.wait_for_event("EC.alert_is_present()","alert apear","no alert"):
            alert = self.browserDriver.switch_to_alert()
            alert.accept()
        else:
            pass

        if platform.system() == "Windows":
            cefChromeDriver = "chromedriver_WIN_2.14.exe"
        elif platform.system() == "Darwin":
            cefChromeDriver = "chromedriver_WIN_2.14"

        optionsCef = webdriver.ChromeOptions()
        optionsCef.debugger_address = "127.0.0.1:14985"
        self.cefDriver = webdriver.Chrome(
            self.findBrowserDriverPath(cefChromeDriver, os.getcwd().split("VE-Tests")[0]), chrome_options=optionsCef)

    def launch_app(self):
        self.test.stop_app = True

    def get_device_time(self):
        time = \
        self.getstatusoutput("ideviceinfo | grep " + " 'TimeIntervalSince1970'")[1].split("TimeIntervalSince1970: ")[
            1].replace("\n", "")
        return float(time)

    def action(self, params, waitUntillReady=True):
        if (waitUntillReady):
            self.test.milestones.getElements(getCurrentScreen=False)
            if self.test.shotByShot:
                self.screenshot_index = self.screenshot_index + 1
                self.test.appium.take_screenshot("shot_" + str(self.screenshot_index).zfill(3), subfolder=True)
        self.test.log(params)
        self.test.milestones.input(params)

    def tapBackground(self):
        self.action({"action": "tap", "pos": [500, 200]})

    def long_tap_background(self):
        self.action({"action": "tap", "duration": 1, "pos": [500, 200]})

    def double_tap(self, x, y):
        self.action({"action": "tap", "tap-count": 2, "pos": [x, y]})

    def get_element_string(self, element, name):
        if name in element:
            return element[name]
        else:
            return ""

    def tap_element(self, element):
        if 'id' not in element:
            self.move_mouse_and_click(element)
        else:
            self.cefDriver.find_elements_by_xpath("//*[@data-milestonesbuttontitle='" + element['id'] + "'][last ()]")[-1].click()

        # self.cefDriver.find_element_by_xpath("//*[@data-milestonesbuttontitle='" + element['id'] + "']").click()

    def move_mouse_and_click(self, element=None):
        from selenium.webdriver import ActionChains

        actions = ActionChains(self.cefDriver)
        if 'x_pos' in element and 'y_pos' in element:
            actions.move_by_offset(element['x_pos'], element['y_pos'])
        else:
            actions.move_by_offset(1, 1)
        actions.perform()
        actions.click()
        actions.perform()

    def tap_center_element(self, element):
        self.tap_element(element)

    def double_tap_element(self, element):
        left = int(element["x_pos"])
        top = int(element["y_pos"])
        width = int(element["width"]) / 2
        height = int(element["height"]) / 2
        label = self.get_element_string(element, "title_text")
        id = self.get_element_string(element, "id")
        self.test.log_assert(isinstance(element, dict))
        self.test.log_assert("x_pos" in element and "y_pos" in element)
        self.action({"action": "tap", "tap-count": 2, "pos": [left + width, top + height], "label": label, "id": id})

    def tap(self, x, y):
        self.action({"action": "tap", "pos": [x, y]})

    def long_tap(self, x, y):
        self.action({"action": "tap", "duration": 1, "pos": [x, y]})

    def get_center_point_and_distance(self, element_name, percent):
        elements = self.test.milestones.getElements()
        element = self.test.milestones.getElement([("name", element_name, "==")], elements)
        self.test.log_assert(isinstance(element, dict))
        width = int(element["width"])
        height = int(element["height"])
        left = int(element["x_pos"]) + (width / 2)
        top = int(element["y_pos"]) + (height / 2)
        distance = (width * percent) / 200
        self.test.log_assert(left or top)
        self.test.log("percent: " + str(percent))
        self.test.log("width: " + str(width) + " height: " + str(height))
        self.test.log("left: " + str(left) + " top:" + str(top) + " distance:" + str(distance))
        return left, top, distance

    def zoom(self, element_name, percent=200, steps=50):
        left, top, distance = self.get_center_point_and_distance(element_name, percent)
        self.action({"action": "zoom", "distance": distance, "step-count": steps, "pos": [left, top]})

    def pinch(self, element_name, percent=200, steps=50):
        left, top, distance = self.get_center_point_and_distance(element_name, percent)
        self.action({"action": "pinch", "distance": distance, "step-count": steps, "pos": [left, top]})

    def notify_sleep(self, duration=0):
        self.action({"action": "sleep", "duration": duration}, waitUntillReady=False)

    def notify_text(self, text, duration=3, color="blue", row=1, alpha=0.5):
        pass

    def log_device_info(self):
        pass

    def take_screenshot(self, description, subfolder=False):
        pass

    def swipe_area(self, start_x, start_y, end_x, end_y, duration=0):
        duration = self.align_duration(duration)
        self.action({"action": "swipe", "start": [start_x, start_y], "end": [end_x, end_y], "duration": duration})

    def scroll(self, start_point, end_point, duration=0):
        duration = self.align_duration(duration)
        self.action({"action": "swipe", "start": [start_point[0], start_point[1]], "end": [end_point[0], end_point[1]],
                     "duration": duration})

    def scroll_from_element(self, element, distance, direction, duration=0):
        start_x, start_y, end_x, end_y, duration = self.generate_scroll_measurements(element, distance, direction,
                                                                                     duration)
        self.action({"action": "swipe", "start": [start_x, start_y], "end": [end_x, end_y], "duration": duration})

    def move_element(self, start_x, start_y, distance, direction, duration=0):
        start_x, start_y, end_x, end_y, duration = self.generate_move_measurements(start_x, start_y, distance,
                                                                                   direction,
                                                                                   duration)
        self.action({"action": "swipe", "start": [start_x, start_y], "end": [end_x, end_y], "duration": duration})

    def swipe_element(self, element, distance, direction, duration=0):
        start_x, start_y, end_x, end_y, duration = self.generate_swipe_measurements(element, distance, direction,
                                                                                    duration)
        self.action({"action": "swipe", "start": [start_x, start_y], "end": [end_x, end_y], "duration": duration})

    def two_fingers_swipe_element(self, element, distance, direction, duration=0, n_stop=2):
        # usage example:
        # utils.appium.two_fingers_swipe_element(hubtv_panel, distance=screen_width / 2, direction="down", duration=0)

        f1_gesture, f2_gesture, duration = self.generate_two_fingers_swipe_measurements(element, distance, direction,
                                                                                        duration)

        self.action({"action": "swipe", "start": [f1_gesture[0], f1_gesture[1]],
                     "end": [f1_gesture[0] + f1_gesture[2], f1_gesture[1] + f1_gesture[3]], "duration": duration,
                     "step-count": n_stop, "finger-count": 2})

    def focus_element(self, element):
        left = int(element["x_pos"])
        top = int(element["y_pos"])
        right = int(element["x_pos"]) + int(element["width"])
        bottom = int(element["y_pos"]) + int(element["height"])
        self.action({"action": "focus", "start": [left, top], "end": [right, bottom]})

    def type_keyboard(self, text, element=None):
        from selenium.webdriver import ActionChains
        actions = ActionChains(self.cefDriver)
        actions.send_keys(text)
        actions.perform()

    def send_backspace(self):
        self.type_keyboard("\b")

    def send_enter(self):
        self.type_keyboard(u'\ue007', "")

    def show_keyboard(self, visible=True):
        self.action({"action": "keyboard", "show": visible})

    def hide_keyboard(self, keyPressed=None):
        self.action({"action": "special-key", "key": keyPressed})

    def in_transition(self):
        result = self.test.milestones.input({"action": "in-transition"})
        if result == "True":
            return True
        return False

    def push_data_to_settings(self, key, value):
        self.getstatusoutput('../tests_framework/appium/changeAppSetting.sh ' + key + ' "' + value + '"')

    def get_element_by_class_name(self, className, index):
        return [className, index]

    def getDeviceId(self):
        pass


    def getDeviceIp(self):
        return None


    def window_size(self):
        device_details = self.test.milestones.getDeviceDetails()
        max_width = device_details["screen-width"] - 1
        max_height = device_details["screen-height"] - 1
        return [max_width, max_height]

class IosWrapper(PlatformWrapper):
    
    def __init__(self, test):
        PlatformWrapper.__init__(self, test)

        from tests_framework.appium.kd_manager import KDManager
        self.test.device_port = "8080"
        self.manager = KDManager(test)

    def get_default_duration(self):
        return 800

    def get_duration_scale(self):
        return 1

    def turn_on_device(self):
        pass

    def codecheck(self):
        pass

    def healthcheck(self):
        self.manager.launch(launchApp=False)

    def send_app_to_background(self):
        self.test.milestones.input({"action" : "pause-app"})
        self.test.wait(0.5)

    def send_app_to_foreground(self):
        self.manager.launch()
        self.test.wait(0.5)

    def reset_app(self):
        pass

    def stop_app(self,logout=True):
        if (logout):
             self.test.milestones.deviceLogout()
        self.test.milestones.input({"action" : "stop-app"})

    def restart_app(self):
        self.stop_app(False)
        self.launch_app()
        pass

    def launch_app(self):
        self.manager.launch()

    def get_device_time(self):
        time = self.os_cmd("ideviceinfo | grep " +" 'TimeIntervalSince1970'").split("TimeIntervalSince1970: ")[1].replace("\n", "")
        return float(time)

    def action(self, params, waitUntillReady=True):
        if(waitUntillReady):
            self.test.milestones.getElements(getCurrentScreen=False)
        self.test.log(params)
        self.test.milestones.input(params)

    def tapBackground(self):
        self.action({"action" : "tap", "pos" : [500,200]})

    def long_tap_background(self):
        self.action({"action" : "tap", "duration" : 1, "pos" : [500,200]})

    def double_tap(self,x,y):
        self.action({"action" : "tap", "tap-count" : 2, "pos" : [x,y]})

    def get_element_string(self, element, name):
        if name in element:
            return element[name]
        else:
            return ""

    def tap_element(self, element):
        left = int(element["x_pos"])
        top = int(element["y_pos"])
        width = int(element["width"])/2
        height = int(element["height"])/2
        label = self.get_element_string(element, "title_text")
        id = self.get_element_string(element, "id")
        self.test.log_assert(isinstance(element, dict), "Element is not dictionary: " + str(element))
        self.action({"action": "tap", "pos": [left+width, top+height], "label": label, "id": id})

    def tap_center_element(self, element):
        self.tap_element(element)

    def double_tap_element(self, element):
        left = int(element["x_pos"])
        top = int(element["y_pos"])
        width = int(element["width"])/2
        height = int(element["height"])/2
        label = self.get_element_string(element, "title_text")
        id = self.get_element_string(element, "id")
        self.test.log_assert(isinstance(element, dict))
        self.test.log_assert("x_pos" in element and "y_pos" in element)
        self.action({"action" : "tap", "tap-count" : 2, "pos" : [left+width, top+height], "label" : label, "id" : id})

    def tap(self,x,y):
        self.action({"action" : "tap", "pos" : [x,y]})

    def long_tap(self,x,y):
        self.action({"action" : "tap", "duration" : 1, "pos" : [x,y]})

    def get_center_point_and_distance(self, element_name, percent):
        elements = self.test.milestones.getElements()
        element = self.test.milestones.getElement([("name", element_name, "==")], elements)
        self.test.log_assert(isinstance(element, dict))
        width = int(element["width"])
        height = int(element["height"])
        left = int(element["x_pos"]) + (width/2)
        top = int(element["y_pos"]) + (height/2)
        distance = (width * percent) / 200
        self.test.log_assert(left or top)
        self.test.log("percent: " + str(percent))
        self.test.log("width: " + str(width) + " height: " + str(height))
        self.test.log("left: " + str(left) + " top:" + str(top) + " distance:" + str(distance))
        return left, top, distance

    def zoom(self, element_name, percent=200, steps=50):
        left, top, distance = self.get_center_point_and_distance(element_name, percent)
        self.action({"action" : "zoom", "distance" : distance, "step-count" : steps, "pos" : [left,top]})

    def pinch(self, element_name, percent=200, steps=50):
        left, top, distance = self.get_center_point_and_distance(element_name, percent)
        self.action({"action" : "pinch", "distance" : distance, "step-count" : steps, "pos" : [left,top]})

    def notify_sleep(self, duration=0):
        self.action({"action" : "sleep", "duration" : duration}, waitUntillReady=False)

    def notify_text(self, text, duration=3, color="blue", row=1, alpha=0.5):
        self.action({"action" : "text", "text" : text, "duration" : duration, "color" : color, "row" : row, "alpha" : alpha}, waitUntillReady=False)

    def log_device_info(self):
        memory = self.test.milestones.getDeviceMemory()
        self.test.log(memory)

    def take_screenshot(self, description, subfolder=False):
        if self.test.screenshotDir and self.test.device_id:
            cmd = 'idevicescreenshot -u ' + self.test.device_id + " " + self.get_folder_path(subfolder) + "/" + self.test.title + "_" + description
            self.os_cmd(cmd, async=self.test.shotByShot)

    def swipe_area(self, start_x, start_y, end_x, end_y, duration=0):
        duration = self.align_duration(duration)
        self.action({"action" : "swipe", "start" : [start_x, start_y], "end" : [end_x, end_y], "duration" : duration})

    def scroll(self, start_point, end_point, duration=0):
        duration = self.align_duration(duration)
        self.action({"action" : "swipe", "start" : [start_point[0], start_point[1]], "end" : [end_point[0], end_point[1]], "duration" : duration})

    def scroll_from_element(self, element, distance, direction, duration=0):
        start_x, start_y, end_x, end_y, duration = self.generate_scroll_measurements(element, distance, direction, duration)
        self.action({"action" : "swipe", "start" : [start_x, start_y], "end" : [end_x, end_y], "duration" : duration})

    def move_element(self, start_x, start_y, distance, direction, duration=0):
        start_x, start_y, end_x, end_y, duration = self.generate_move_measurements(start_x, start_y, distance, direction, duration)
        self.action({"action" : "swipe", "start" : [start_x, start_y], "end" : [end_x, end_y], "duration" : duration})

    def swipe_element(self, element, distance, direction, duration=0):
        start_x, start_y, end_x, end_y, duration = self.generate_swipe_measurements(element, distance, direction, duration)
        self.action({"action" : "swipe", "start" : [start_x, start_y], "end" : [end_x, end_y], "duration" : duration})

    def two_fingers_swipe_element(self, element, distance, direction, duration=0, n_stop=2):
        # usage example:
        # utils.appium.two_fingers_swipe_element(hubtv_panel, distance=screen_width / 2, direction="down", duration=0)

        f1_gesture, f2_gesture, duration = self.generate_two_fingers_swipe_measurements(element, distance, direction, duration)

        self.action({"action" : "swipe", "start" : [f1_gesture[0], f1_gesture[1]], "end" : [f1_gesture[0] + f1_gesture[2], f1_gesture[1] + f1_gesture[3]], "duration" : duration, "step-count" : n_stop, "finger-count" : 2})

    def focus_element(self, element):
        left = int(element["x_pos"])
        top = int(element["y_pos"])
        right = int(element["x_pos"]) + int(element["width"])
        bottom = int(element["y_pos"]) + int(element["height"])
        self.action({"action" : "focus", "start" : [left, top], "end" : [right, bottom]})

    def type_keyboard(self, text, element=None):
        assert isinstance(text, basestring)

        self.action({"action" : "type", "text" : text, "element" : element})

    def send_backspace(self):
        self.type_keyboard("\b")

    def send_enter(self):
        self.hide_keyboard('Go')

    def show_keyboard(self, visible=True):
        self.action({"action" : "keyboard", "show" : visible})

    def hide_keyboard(self, keyPressed=None):
        self.action({"action" : "special-key", "key" : keyPressed})

    def in_transition(self):
        result = self.test.milestones.input({"action" : "in-transition"})
        if result == "True":
            return True
        return False

    def push_data_to_settings(self, key, value):
        self.os_cmd('../tests_framework/appium/changeAppSetting.sh ' + key + ' "' + value +'"')

    def getDeviceId(self):
        self.test.devices = []
        deviceId = None
        p = os.popen('ios-deploy -c -t 1',"r")
        p.readline()
        while True:
            line = p.readline()
            if not line:
                break
            regResult = re.search("(\([a-z|0-9]).*\)",line)
            if regResult:
                deviceId = regResult.group()
                deviceId = deviceId[1:-1]
                self.test.devices.append(deviceId)
                self.test.log("Found device id: " + deviceId)
        p.close()
        self.test.log("Finished retrieving device id's")
        device_index = 0
        device_number = pytest.config.getoption("--device-number")
        if device_number:
            device_index = int(device_number)
        self.test.log_assert(device_index < len(self.test.devices), "iOS Device number " + str(device_index) + " exceeded available ios devices connected = " + str(len(self.test.devices)) + ", devices found: " + str(self.test.devices))
        deviceId = self.test.devices[device_index]
        self.test.device_index = device_index
        self.test.log("using device index #" + str(device_index) + "=" + deviceId)
        return deviceId

    def getDeviceIp(self):
        return None

    def window_size(self):
        device_details = self.test.milestones.getDeviceDetails()
        max_width = device_details["screen-width"] -1
        max_height = device_details["screen-height"] - 1
        return [max_width,max_height]

class AndroidWrapper(PlatformWrapper):
    
    def __init__(self, test):
        PlatformWrapper.__init__(self, test)
        if self.test.project == "KD":
            self.test.device_port = "5050"
        else:
            self.test.device_port = "8080"
        if 'appium' in self.configurations:
            self.test.use_appium = True
        elif self.test.project == "KD":
            self.configurations['appium'] = {}
            self.configurations['appium']['appPackage'] = 'com.vodafone.pearlandroid'
            self.configurations['appium']['appActivity'] = 'com.cisco.veop.client.MainActivity'
        elif self.test.project == "NET":
            self.configurations['appium'] = {}
            self.configurations['appium']['appPackage'] = 'com.cisco.videoeverywhere4.nexplayer'
            self.configurations['appium']['appActivity'] = 'com.cisco.veop.client.MainActivity'
        else:
            self.configurations['appium'] = {}
            self.configurations['appium']['appPackage'] = 'com.cisco.videoeverywhere3.nexplayer'
            self.configurations['appium']['appActivity'] = 'com.cisco.veop.client.MainActivity'

    def start_server(self):
        configurations = self.configurations
        desired_caps = {}
        desired_caps['udid'] = self.test.device_id
        desired_caps['platformName'] = configurations["appium"]["platformName"]
        desired_caps['platformVersion'] = configurations["appium"]["platformVersion"]
        desired_caps['deviceName'] = self.test.device_id
        desired_caps['appPackage'] = configurations["appium"]["appPackage"]
        desired_caps['appActivity'] = configurations["appium"]["appActivity"]
        desired_caps['autoLaunch'] = configurations["appium"]["autoLaunch"] == "True"
        desired_caps['newCommandTimeout'] = configurations["appium"].get("newCommandTimeout", 3600)

        if "runAppiumServer" in self.configurations["appium"] and self.configurations["appium"]["runAppiumServer"] == "True":
            for nodeIndex in range(0, 3):
                os.system("killall node")
            self.start_appium_server(self.configurations["appium"]["ip"])

        from appium import webdriver
        self.driver = webdriver.Remote('http://' + self.configurations["appium"]["ip"]+'/wd/hub', desired_caps)

    def get_default_duration(self):
        return 1600

    def get_duration_scale(self):
        return 2

    def type_keyboard(self, text):
        self.wait_for_ready()
        self.test.log_assert(isinstance(text, basestring))
        command = "adb -s " + self.test.device_id + " shell input text " + text.replace(" ","%s")
        self.os_cmd(command)
    
    def key_event(self, keycode, metastate=None, waitForReady=True):
        if waitForReady:
            self.wait_for_ready()
        self.os_cmd("adb -s " + self.test.device_id + " shell input keyevent " + str(keycode))

    def key_event_adb(self, keycode, waitForReady=True):
        if waitForReady:
            self.wait_for_ready()
        self.os_cmd("adb -s " + self.configurations["device"]["deviceId"] + " shell input keyevent " + str(keycode))

    def long_key_event(self, keycode, waitForReady=True):
        if waitForReady:
            self.wait_for_ready()
        self.os_cmd("adb -s " + self.configurations["device"]["deviceId"] + " shell input keyevent --longpress " + str(keycode))


    def back(self):
        self.key_event("4")
            
    def is_device_on(self):
        status = self.os_cmd("adb -s " + self.test.device_id +" shell \"dumpsys power | grep mWakefulness=\"").split("=")[1]
        return status.replace("\r", "").replace("\n", "") == "Awake"
    
    def turn_on_device(self):
        if not self.is_device_on():
            self.key_event("26", waitForReady=False)

    def codecheck(self):
        pass

    def healthcheck(self):
        pass

    def reset_app(self):
        self.test.log_assert(self.test.device_id, "Cannot find device identifier")
        self.test.log_assert(self.configurations["appium"]["appPackage"], "Cannot find application package name")
        self.os_cmd("adb -s " + self.test.device_id + " shell pm clear " + self.configurations["appium"]["appPackage"])

    def get_app_arguments(self):
        args = ""
        if self.test.overrideArgs:
            he = self.test.configuration['he']
            if he:
                if 'csds' in he:
                    args += " --es csds_url " + he['csds']
    #            if 'subnet' in he:
    #                args += " --es sgw_url " + "drm-sgw-sgw." + he['subnet'] + ".phx.cisco.com"
            if self.test.is_dummy:
                args += " --es dummy True"
            self.test.log("app arguments: " + args)
        return args

    def wait_for_ready(self):
        self.test.milestones.getElements()
        if self.test.shotByShot:
            self.screenshot_index = self.screenshot_index + 1
            self.test.appium.take_screenshot("shot_" + str(self.screenshot_index).zfill(3), subfolder=True)
            
    def tap(self, x, y):
        self.wait_for_ready()
        self.test.log_assert(isinstance(x, int) or isinstance(y, int))
        self.os_cmd("adb -s " + self.test.device_id + " shell input tap " + str(x) + " " + str(y))
        
    def tap_element(self, element):
        self.wait_for_ready()
        self.test.log_assert(isinstance(element, dict), "Element is not a dictionary, element: " + str(element))
        self.test.log_assert("x_pos" in element and "y_pos" in element and "width" in element and "height" in element)
        self.test.log("Tapping element: " + str(element))
        self.tap(int(element["x_pos"]) + int(element["width"])/3, int(element["y_pos"]) + (int(element["height"])/10))

    def tap_center_element(self, element):
        self.wait_for_ready()
        self.test.log_assert(isinstance(element, dict), "Element is not a dictionary, element: " + str(element))
        self.test.log_assert("x_pos" in element and "y_pos" in element and "width" in element and "height" in element)
        self.test.log("Tapping center of element: " + str(element))
        self.tap(int(element["x_pos"]) + (int(element["width"])/2), int(element["y_pos"]) + (int(element["height"])/2))

    def scroll_from_element(self, element, distance, direction, duration=0):
        self.wait_for_ready()
        start_x, start_y, end_x, end_y, duration = self.generate_scroll_measurements(element, distance, direction, duration)
        self.os_cmd("adb -s " + self.test.device_id + " shell input swipe " + str(start_x) + " " + str(start_y) + " " + str(end_x) + " " + str(end_y) + " " + str(duration))

    def move_element(self, start_x, start_y, distance, direction, duration=0):
        self.wait_for_ready()
        start_x, start_y, end_x, end_y, duration = self.generate_move_measurements(start_x, start_y, distance, direction, duration)
        self.os_cmd("adb -s " + self.test.device_id + " shell input swipe " + str(start_x) + " " + str(start_y) + " " + str(end_x) + " " + str(end_y) + " " + str(duration))

    def swipe_element(self, element, distance, direction, duration=0):
        self.wait_for_ready()
        self.test.log_assert(isinstance(element, dict), "Element is not a dictionary, element: " + str(element))
        start_x, start_y, end_x, end_y, duration = self.generate_swipe_measurements(element, distance, direction, duration)
        self.os_cmd("adb -s " + self.test.device_id + " shell input swipe " + str(start_x) + " " + str(start_y) + " " + str(end_x) + " " + str(end_y) + " " + str(duration))

    def notify_sleep(self, duration=0):
        pass

    def notify_text(self, text, duration=3, color="blue", row=0, alpha=0.5):
        pass

    def log_device_info(self):
        pass

    def take_screenshot(self, description, subfolder=False):
        if self.test.screenshotDir and self.test.device_id:
            cmd = "adb -s " + self.test.device_id + " shell screencap -p | perl -pe \'s/\\x0D\\x0A/\\x0A/g\' > " + self.get_folder_path(subfolder) + "/" + self.test.title + "_" + description + ".png"
            self.os_cmd(cmd, async=self.test.shotByShot)

    def swipe_area(self, start_x, start_y, end_x, end_y, duration=0):
        self.wait_for_ready()
        duration = self.align_duration(duration)
        self.os_cmd("adb -s " + self.test.device_id + " shell input swipe " + str(start_x) + " " + str(start_y) + " " + str(end_x) + " " + str(end_y) + " " + str(duration))

    def send_backspace(self):
        self.wait_for_ready()
        self.key_event(ANDROID_KEYCODE_DEL)

    def send_enter(self):
        self.wait_for_ready()
        self.key_event(ENTER_KEY_CODE)

    '''return UTC timestamp in seconds'''
    def get_device_time(self):
        time = self.os_cmd("adb -s " + self.test.device_id + " shell date +%s")
        return int(time[1])

    def launch_app(self):
        if self.driver:
            self.driver.launch_app()

        cmd = "adb -s " + self.test.device_id + " shell am start -S -W -a android.intent.action.MAIN -c android.intent.category.LAUNCHER -n " + self.configurations["appium"]["appPackage"] + "/" + self.configurations["appium"]["appActivity"]
        cmd += self.get_app_arguments()
        self.os_cmd(cmd)
        self.test.stop_app = True

    def close_app(self):
        if self.driver:
            self.driver.close_app()
        else:
            cmd = "adb  -s " + self.test.device_id + " shell am force-stop " + self.configurations["appium"]["appPackage"]
            self.os_cmd(cmd)

    def stop_app(self,logout=True):
        self.close_app()
        if self.driver:
            self.driver.quit()
        if "runAppiumServer" in self.configurations["appium"] and self.configurations["appium"]["runAppiumServer"] == "True":
            self.close_appium_server()

    def send_app_to_background(self):
        self.key_event(3)
        self.test.wait(0.5)

    def send_app_to_foreground(self):
        self.os_cmd("adb -s " + self.test.device_id + " shell am start -W -n " + self.configurations["appium"]["appPackage"] + "/" + self.configurations["appium"]["appActivity"])
        self.test.wait(0.5)
        self.wait_for_ready()

    def restart_app(self):
        self.close_app()
        self.launch_app()
        self.wait_for_ready()

    def push_data_to_settings(self, key, value):
        self.close_app()
        self.os_cmd('adb -s ' + self.test.device_id +
                        ' shell am start -W -S -a android.intent.action.VIEW -c android.intent.category.DEFAULT -n ' +
                        self.configurations["appium"]["appPackage"] + '/com.cisco.veop.client.SettingsActivity -e ' + key + ' "' + value +'"')

    def two_fingers_swipe_element(self, element, distance, direction, duration=0, n_stop=2):
        from appium.webdriver.common.touch_action import TouchAction
        from appium.webdriver.common.multi_action import MultiAction
        # usage example:
        # utils.appium.two_fingers_swipe_element(hubtv_panel, distance=screen_width / 2, direction="down", duration=0)

        self.wait_for_ready()
        f1_gesture, f2_gesture, duration = self.generate_two_fingers_swipe_measurements(element, distance, direction, duration)

        a1 = TouchAction(self.driver)
        a2 = TouchAction(self.driver)
        a1.press(x=f1_gesture[0], y=f1_gesture[1])
        a2.press(x=f2_gesture[0], y=f2_gesture[1])

        for i in range(1, n_stop):
            a1.move_to(x=f1_gesture[2]/n_stop, y=f1_gesture[3]/n_stop)
            a2.move_to(x=f2_gesture[2]/n_stop, y=f2_gesture[3]/n_stop)
        a1.release()
        a2.release()

        ma = MultiAction(self.driver)
        ma.add(a1, a2)
        ma.perform()

    def in_transition(self):
        return False

    def double_tap_element(self, element):
        self.wait_for_ready()
        width = int(element["width"])/2
        height = int(element["height"])/2
        self.test.log_assert(isinstance(element, dict))
        self.test.log_assert("x_pos" in element and "y_pos" in element)
        self.driver.execute_script("mobile: tap",{ "touchCount": 2, "x": int(element["x_pos"])+width, "y":int(element["y_pos"])+height})

    def getDeviceId(self):
        if os.name == 'nt' or os.name == 'posix':
            devices = self.os_cmd("adb devices")
            devices_regex = re.compile(r"\n(?P<id>[A-Za-z0-9]*?)\s")
            res = devices_regex.findall(devices)
            device_list = res if res else None
        else:
            device_list = self.os_cmd("adb devices | grep -v List | cut -f 1").split()
        self.test.log_assert(device_list and len(device_list), "Cannot find an android device attached")
        self.test.log("device_list: " + str(device_list))
        device_id = None
        for device_item in device_list:
            if device_item:
                device_id = device_item
        return device_id

    def getDeviceIp(self):
        if os.name == 'nt' or os.name == 'posix':
            import re
            ip_route = self.os_cmd("adb shell ip route")
            ip_regex = re.compile(r"wlan0.*src\s(?P<ip>.*?)\s")
            res = ip_regex.findall(ip_route)
            device_ip = res[0] if res else None
        else:
            device_ip = self.test.appium.os_cmd("adb shell ip route | grep wlan0 | grep -o 'src [^ ]*' | cut -b5- | uniq").rstrip()
        self.test.log_assert(device_ip, "Cannot find android device ip via device (maybe the device is not on wifi)")
        return device_ip + ":" + self.test.device_port

    def zoom(self, element_name, percent=200, steps=50):
        self.wait_for_ready()
        element = self.driver.find_element_by_accessibility_id(element_name)
        self.driver.zoom(element, percent, steps)
        self.test.wait(0.8)

    def pinch(self, element_name, percent=200, steps=50):
        self.wait_for_ready()
        element = self.driver.find_element_by_accessibility_id(element_name)
        self.driver.pinch(element, percent, steps)
        self.test.wait(0.8)

    def start_appium_server(self, ip="127.0.0.1:4723"):
        host, port = ip.split(":")
        self.appium_server_process = Popen("appium -a " + host + " -p " + port + " -bp " + str(int(port)+1000), shell=True, preexec_fn=setsid)
        sleep(APPIUM_INIT_TIMEOUT)

    def close_appium_server(self):
        killpg(self.appium_server_process.pid, SIGTERM)

    def window_size(self):
        device_details = self.test.milestones.getDeviceDetails()
        max_width = device_details["screen-width"] - 1
        max_height = device_details["screen-height"] - 1
        return [max_width,max_height]

    def wifi_connect(self, state=True):
        if state:
            cmd = " shell am broadcast -a WifiChange -c android.intent.category.DEFAULT -n com.cisco.blizzardcfg/.WifiStateChange -e wifi true"
        else:
            cmd = " shell am broadcast -a WifiChange -c android.intent.category.DEFAULT -n com.cisco.blizzardcfg/.WifiStateChange -e wifi false"
        self.os_cmd("adb -s " + self.test.device_id + cmd)
