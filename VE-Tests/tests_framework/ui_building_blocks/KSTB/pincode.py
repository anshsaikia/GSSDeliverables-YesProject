__author__ = 'upnidhi'

import logging
from time import sleep
from tests_framework.ui_building_blocks.screen import Screen, ScreenActions
from tests_framework.milestones.milestones_client import MilestonesClient
from tests_framework.he_utils import he_utils
import json
import time
from tests_framework.ui_building_blocks.KSTB.action_menu import ActionMenu

'''Constants'''
TIMEOUT = 2


class PinCodeActionMenu(ActionMenu):
    YOUTH_LIMIT_RATING = 16

    def __init__(self, test):
        ActionMenu.__init__(self, test)

    def verifyPinScreen(self):
        self.verify_active()

    def enter_pin(self, youthpin):
        screen = self.test.milestones.get_current_screen()
        if screen == "pincode":
            "Enter Pin"
        if self.test.platform == "Android":
            element = self.test.milestones.getElement([("name", "edit_text","==" )])
            self.test.log_assert(element)
            self.test.appium.tap_element(element)
            sleep(0.5)
            self.test.appium.type_keyboard(youthpin)
        else:
            #app_element = self.test.appium.get_element_by_class_name('UIASecureTextField', 0)
            self.test.appium.hide_keyboard(youthpin[0])
            self.test.appium.hide_keyboard(youthpin[1])
            self.test.appium.hide_keyboard(youthpin[2])
            self.test.appium.hide_keyboard(youthpin[3])

            sleep(TIMEOUT)

    def verify_message(self):
        element = self.test.milestones.getElement([("name", "message_text","==" )])
       # assert element.partition(' ')[0] == "WRONG"

    def verify_pin_entry_disabled(self):
        pin_entry_enabled = self.test.milestones.getElement("pincode_entry_enabled")
        self.test.log_assert(pin_entry_enabled == False,"Pin entry not disabled")

    def find_pin_code_event(self):
        #get the server data information
        #check all those who returns yp
        return;

    def enter_correct_pincode(self):
        """
        Considering 1111 is the pincode
        Enter 1111
        """
        self.test.appium.key_event("KEYCODE_DPAD_CENTER")
        self.test.wait(2)
        self.test.appium.key_event("KEYCODE_DPAD_CENTER")
        self.test.wait(2)
        self.test.appium.key_event("KEYCODE_DPAD_CENTER")
        self.test.wait(2)
        self.test.appium.key_event("KEYCODE_DPAD_CENTER")
        self.test.wait(2)

    def enter_incorrect_pincode(self):
        """
        Considering 1111 is the pincode
        Enter 2222
        """
        self.test.appium.key_event("KEYCODE_DPAD_RIGHT")
        self.test.wait(2)
        self.test.appium.key_event("KEYCODE_DPAD_CENTER")
        self.test.wait(2)
        self.test.appium.key_event("KEYCODE_DPAD_CENTER")
        self.test.wait(2)
        self.test.appium.key_event("KEYCODE_DPAD_CENTER")
        self.test.wait(2)
        self.test.appium.key_event("KEYCODE_DPAD_CENTER")
        self.test.wait(2)

    def enter_pincode(self, key_events):
        """
        key_events: array of key events
        """
        for key_event in key_events:
            self.test.appium.key_event(key_event)
            self.test.wait(1)