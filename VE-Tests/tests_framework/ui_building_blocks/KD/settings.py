___author__ = 'bwarshaw'

from time import sleep
from tests_framework.ui_building_blocks.screen import Screen
from tests_framework.ui_building_blocks.screen import ScreenActions

import logging

'''Constants'''

class Settings(Screen):
    def __init__(self, test):
        Screen.__init__(self, test, "settings")

    def navigate(self):
        logging.info("Navigate to settings")
        screen = self.test.milestones.get_current_screen()
        if screen == "settings":
            return

        if self.test.project != "KD" and self.test.app_mode == "V2":
            if not self.test.ui.element_exists("settings"):
                self.test.screens.tv_filter.navigate()
            self.test.ui.tap_element("settings")
        else:
            self.test.screens.main_hub.navigate()
            settings_dic_value = self.test.milestones.get_dic_value_by_key("DIC_SETTINGS_SETTINGS","general")
            settings_button = self.test.milestones.getElement([("title_text", settings_dic_value.upper(), "==")])
            self.test.log_assert(settings_button, "Cannot find settings button: " + settings_dic_value)
            self.test.appium.tap_element(settings_button)

        self.verify_active()

    def open_legal(self):
        self.navigate()

        logging.info("Opening Legal Menu")
        help_dic_value = self.test.milestones.get_dic_value_by_key("DIC_SETTINGS_LEGAL_INFORMATION","general")
        help_button = self.test.milestones.getElement([("title_text", help_dic_value, "==")])
        self.test.appium.tap_element(help_button)

    def open_data_privacy(self):
        self.navigate()

        logging.info("Opening Data Privacy link")
        privacy_dic_value = self.test.milestones.get_dic_value_by_key("DIC_HELP_SETTINGS_DATA_SECURITY_INFO","general")
        privacy_button = self.test.milestones.getElement([("title_text", privacy_dic_value, "==")])
        self.test.appium.tap_element(privacy_button)

    def open_help(self):
        self.navigate()

        logging.info("Opening Help Menu")
        help_dic_value = self.test.milestones.get_dic_value_by_key("DIC_SETTINGS_HELP","general")
        help_button = self.test.milestones.getElement([("title_text", help_dic_value, "==")])
        self.test.appium.tap_element(help_button)

    #scroll horizontally
    def scroll(self,fromElement,toElement):

        start_x = fromElement['x_pos']
        start_y = fromElement['y_pos']

        stop_x = toElement['x_pos']
        stop_y = toElement['y_pos']

        self.test.appium.swipe_area(start_x, start_y, stop_x, stop_y)

    def log_out(self):
        self.navigate()
        # SWIPE AREA

        window_width, window_height = self.test.milestones.getWindowSize()
        x = window_width/2
        upper_y = window_height*0.8
        lower_y = window_height*0.9
        for i in range(0, 100):
            self.test.mirror.swipe_area(x, lower_y,x, upper_y)
            sign_out_button = self.test.milestones.getElementByDic("DIC_SETTINGS_SIGN_OUT", "DIC_SETTINGS_LOGOUT")
            if sign_out_button:
                break

        self.test.log_assert(sign_out_button, "Cannot find sign out or log out element")
        self.test.appium.tap_element(sign_out_button)

        #Second Tap
        self.test.wait(5)
        sign_out_button = self.test.milestones.getElementByDic("DIC_SETTINGS_LOGOUT_ARE_YOU_SURE", "DIC_GENERIC_YES")
        self.test.log_assert(sign_out_button, "Cannot find sign out button")
        self.test.appium.tap_element(sign_out_button)
        login_screen = self.test.screens.login_screen
        self.test.log_assert(login_screen.is_active(timeout=5), "Login Screen Didn't come up within 5 sec")

    def device_info(self,verify = True):
        self.navigate()
        logging.info("Opening Device info screen")
        dev_info_dic_value = self.test.milestones.get_dic_value_by_key("DIC_SETTINGS_DEVICE_INFO","general").upper()
        sleep(5)
        dev_info_button = self.test.milestones.getElement([("title_text", dev_info_dic_value, "==")])
        self.test.appium.tap_element(dev_info_button)
        if(verify==True):
            self.compare_device_Info_HeadAndVal()

    def compare_device_Info_HeadAndVal(self):
        self.test.wait(1)
        device_details_milestones = self.test.milestones.getDeviceDetails()
        deviceId = device_details_milestones['drm-device-id']
        hh_id = self.test.configuration["he"]["generated_household"]
        acc_id = self.test.configuration["he"]["generated_username"]
        devInfoLabelExpected  = self.test.milestones.get_dic_value_by_key("DIC_SETTINGS_DEVICE_INFO_DEVICE_ID","general")
        if self.test.project=='KD':
            devInfoLabelPresented = self.test.milestones.getElement([("title_text", devInfoLabelExpected, "==")])
        else:
            devInfoLabelPresented = self.test.milestones.getElement([("DeviceIdText", devInfoLabelExpected, "==")])
            self.test.log_assert(devInfoLabelPresented, "Cannot find device id label: " + devInfoLabelExpected)

        if self.test.project=='KD':
            devInfoValuePresented = self.test.milestones.getElement([("title_text", deviceId, "==")])
        else:
            devInfoValuePresented = self.test.milestones.getElement([("DeviceIdValue", deviceId, "==")])
        self.test.log_assert(devInfoValuePresented, "Cannot find device id value: " + deviceId)

        devInfoLabelExpected  = self.test.milestones.get_dic_value_by_key("DIC_SETTINGS_DEVICE_INFO_HOUSEHOLD","general")
        if self.test.project=='KD':
            devInfoLabelPresented = self.test.milestones.getElement([("title_text", devInfoLabelExpected, "==")])
        else:
            devInfoLabelPresented = self.test.milestones.getElement([("HouseHoldIdText", devInfoLabelExpected, "==")])
        self.test.log_assert(devInfoLabelPresented, "Cannot find Household label: " + devInfoLabelExpected)
        if self.test.project=='KD':
            devInfoValuePresented = self.test.milestones.getElement([("title_text", hh_id, "==")])
        else:
            devInfoValuePresented = self.test.milestones.getElement([("HouseHoldIdValue", hh_id, "==")])
        self.test.log_assert(devInfoValuePresented, "Cannot find household id value: " + hh_id)

        devInfoLabelExpected  = self.test.milestones.get_dic_value_by_key("DIC_SETTINGS_DEVICE_INFO_ACCOUNT_ID","general")
        if self.test.project=='KD':
            devInfoLabelPresented = self.test.milestones.getElement([("title_text", devInfoLabelExpected, "==")])
        else:
            devInfoLabelPresented = self.test.milestones.getElement([("AccountIdText", devInfoLabelExpected, "==")])

        if self.test.project=='KD':
            if(devInfoLabelPresented==None):
                #we have to scroll apparently it is not in screen
                elements = self.test.milestones.getElements()
                firstElement = self.test.milestones.getElement([("id", "DeviceIdText", "==")], elements)
                distanceEl = self.test.milestones.getElement([("name", "events_scroller", "==")], elements)
                distance = distanceEl["width"]
                direction = ScreenActions.LEFT
                self.test.appium.scroll_from_element(firstElement,distance,direction,0)
                devInfoLabelPresented = self.test.milestones.getElement([("title_text", devInfoLabelExpected, "==")])
        self.test.log_assert(devInfoLabelPresented, "Cannot find Account label: " + devInfoLabelExpected)
        if self.test.project=='KD':
            devInfoValuePresented = self.test.milestones.getElement([("title_text", acc_id, "==")])
        else:
            devInfoValuePresented = self.test.milestones.getElement([("AccountIdValue", acc_id, "==")])
        self.test.log_assert(devInfoValuePresented, "Cannot find Account id value: " + acc_id)


    def verify_parental_control_state_locked(self):
        elements = self.test.milestones.getElements()
        lock_button = self.test.milestones.getElement([("name", "parental_control_lock_unlock_button", "==")], elements)
        self.test.log_assert(lock_button, "No Lock button in milestone of current screen")
        if lock_button['is_locked']:
            return True
        else:
            return False

