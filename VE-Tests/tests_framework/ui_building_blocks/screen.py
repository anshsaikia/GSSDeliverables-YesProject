__author__ = 'bwarshaw'

from enum import Enum
import logging

BACK_TIMEOUT = 1

class ScreenActions(Enum):
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"

class ScreenDismiss(Enum):
    TAP = "tap"
    TIMEOUT = "timeout"
    CLOSE_BUTTON = "closeButton"
    BACK_BUTTON = "backButton"
    TAP_ON_EVENT = "tapOnEvent"

class Screen(object):
    actionTypes = ScreenActions
    dismissTypes = ScreenDismiss

    def __init__(self, test, screen_name=None):
        self.test = test
        self.extension = screen_name == None
        self.screen_name = screen_name
        if not self.extension:
            self.test.screens.screen_list[screen_name] = self

    def screen(self):
        if self.extension:
            return self.test.getCurrentScreen()
        else:
            return self

    def is_supported(self):
        self.test.log_assert(not self.extension, "Extension does not support this method")
        is_supported = False
        if self.test.supported_screens:
            if self.screen_name in self.test.supported_screens:
                is_supported = True
        else:
            is_supported = True
        return is_supported

    def set_parents(self, *parents):
        self.parents = parents
        self.children = []
        for parent in parents:
            parent.children.append(self)

    def wait_untill_not_active(self, timeout=60):
        self.test.log_assert(not self.extension, "Extension does not support this method")
        current_screen = self.test.milestones.get_current_screen()
        if current_screen != self.screen_name:
                return False
        msec = 1.0
        count = int(timeout/msec)
        self.test.log("waiting for " + self.screen_name + " to be closed")
        for i in range(count):
            self.test.wait(msec, log=False)
            current_screen = self.test.milestones.get_current_screen()
            if current_screen != self.screen_name:
                return True

        return False

    def is_active(self, timeout=0, bootmode = False, ignoreNotification=False):
        self.test.log_assert(not self.extension, "Extension does not support this method")
        notification = self.test.screens.notification
        current_screen = self.test.milestones.get_current_screen()
        if current_screen == self.screen_name:
                return True
        msec = 0.1
        if timeout > 0:
            count = int(timeout/msec)
        else:
            count = 1
        self.test.log("checking if " + self.screen_name + " is active for timeout " + str(timeout))
        for i in range(count):
            current_screen = self.test.milestones.get_current_screen()
            if ignoreNotification and current_screen == notification.screen_name:
                logging.info("dismissing notification")
                notification.dismiss_notification()
                #Goback to fullscreen if info layer is active
                self.test.screens.infolayer.dismiss(ScreenDismiss.TAP)
            if current_screen == self.screen_name:
                logging.info("is_active=YES for %s", current_screen)
                return True
            if bootmode == True and (current_screen != "boot" and current_screen != "login" and current_screen != "False" and current_screen != "fullscreen"):
                logging.info("bootmode error, current screen for %s", current_screen)
                return False

            count = count -1
            if count <= 0:
                break
            self.test.wait(msec, log=False)

        logging.warning("is_active=NO: expected=%s, found=%s", self.screen_name, current_screen)
        return False

    def verify_not_active(self, timeout=30, ignoreNotification=False):
        self.test.log_assert(not self.extension, "Extension does not support this method")
        is_active = self.is_active(timeout, ignoreNotification=ignoreNotification)
        if (is_active == True):
            if self.test.milestones.get_current_screen() == "notification":
                self.test.log_assert(False, "received notification: " + self.test.screens.notification.get_notification_message() + "' but should not be active")
            else:
                self.test.log_assert(is_active, "Current screen should not be active")

    def verify_active(self, timeout=30, ignoreNotification=False):
        self.test.log_assert(not self.extension, "Extension does not support this method")
        is_supported = self.is_supported()
        is_active = self.is_active(timeout, ignoreNotification=ignoreNotification)
        if (is_active == False):
            if self.test.milestones.get_current_screen() == "notification":
                self.test.log_assert(False, "received notification: " + self.test.screens.notification.get_notification_message() + "' but expected screen is: '" + self.screen_name + "'")
            elif is_supported:
                self.test.log_assert(is_active, "Expected screen is: '" + self.screen_name + "'")
            else:
                self.test.log_assert(is_active, "Expected screen is: '" + self.screen_name + "' which is not in the supported screens")

    def go_to_previous_screen(self):
        screen = self.test.milestones.get_current_screen()
        self.test.log("--------Going Back -------- from " + screen)

        if screen == "main_hub" or screen == "fullscreen":
            pass
        elif screen == "notification" and self.test.platform == "iOS":
            pass
        else:
            elements = self.test.milestones.getElements()

            back_element = self.test.milestones.getElement([("id", "back", "==")], elements)

            # using the id=back should be the right way but we don't want to break anythings
            if back_element is None:
                back_element = self.test.milestones.getElement([("title_text", "BACK", "_)")], elements)

            if back_element is None:
                back_element = self.test.milestones.getElement([("id", "exit", "==")], elements)

            self.test.log_assert(back_element, "Back button not Found")
            self.test.appium.tap_element(back_element)
            self.test.wait(BACK_TIMEOUT)

            screen = self.test.milestones.get_current_screen()
            self.test.log("Navigated via back button to " + screen)

    def dismiss_notification(self, ignoreScreenQuery=False):
        current_screen = None
        if not ignoreScreenQuery:
            current_screen = self.test.milestones.get_current_screen()
        if ignoreScreenQuery or current_screen == "notification":
            for notification_index in range(0, 2):
                self.test.screens.notification.dismiss()
                self.test.wait(1)
                current_screen = self.test.milestones.get_current_screen()
                if current_screen != "notification":
                    break
        self.test.screens.notification.verify_not_active(timeout=0)

    def tap_search(self):
        elements = self.test.milestones.getElements()
        search_element = self.test.milestones.getElement([("title_text", "SEARCH", "==")], elements)
        self.test.log_assert(search_element,"Search button not Found")
        self.test.appium.tap_element(search_element)

    def is_program_locked(self):
        current_screen = self.test.milestones.get_current_screen()
        if current_screen == 'infolayer' or current_screen == 'fullscreen':
            unlock_dic_value = self.test.milestones.get_dic_value_by_key("DIC_INFO_LAYER_UNLOCK_BUTTON").upper()
        else:
            unlock_dic_value = self.test.milestones.get_dic_value_by_key("DIC_ACTION_MENU_UNLOCK_BUTTON").upper()
        unlock_button =  self.test.milestones.getElement([("title_text", unlock_dic_value, "==")])
        if unlock_button:
            return unlock_button
        return False

    def tap_unlock_program(self):
        unlock_button = self.is_program_locked()
        self.test.log_assert(unlock_button, "Program is not Locked. No Unlock button on the Screen")
        self.test.appium.tap_element(unlock_button)

    def verify_notification_message(self, key):
        dic_value_msg = self.test.milestones.get_dic_value_by_key(key, "error")
        notification_element = self.test.milestones.getElement([("title_text", dic_value_msg, "==")])
        self.test.log_assert(notification_element,"Notification message: " + dic_value_msg + "is not found in screen")
        return notification_element

