__author__ = 'mibenami'
from enum import Enum
from tests_framework.ui_building_blocks.screen import Screen

class NotificationStrings(Enum):
    STOP_RECORDING = "Are you sure that you want to stop this recording?"
    DELETE_RECORDING   = "Are you sure that you want to delete this recording?"
    AUTH_ERROR = "You are not subscribed to this channel, call customer care to subscribe .(ERR-008)"
    DIC_ERROR_PLAYBACK_CONCURRENCY = "You have exceeded the maximum number of simultaneous video streams for your household. If you want to start the Video on this device, you must stop the stream on another device in your household.(ERR-002)"


class Notification(Screen):

    def __init__(self, test):
        Screen.__init__(self, test, "notification")

    def get_notification(self, elements=None):
        if elements is None:
            elements = self.test.milestones.getElements()
        notification = None
        for element in elements:
            if ('name' in element and element['name'] == 'NotificationView'):
                notification = element
                return notification
        return notification

    def dismiss(self):
        elements = self.test.milestones.getElements()
        notification = self.test.screens.notification.get_notification_message(elements)
        if notification:
            self.test.log("dismissing notification: " + notification)
            if self.test.platform == "iOS" and self.test.app_mode != "V2":
                message_element = self.test.milestones.getElement([("title_text", "DISMISS ALL TIPS", "==")], elements)
                if not message_element:
                    message_element = self.test.milestones.getElement([("id", "MESSAGE", "==")], elements)
                self.test.log_assert(message_element,"Notification dismissal not found on notification: " + notification)
                self.test.wait(3)
                self.test.say('closing notification')
                self.test.appium.tap_element(message_element)
            else:
                if self.test.project != "KD" and self.test.app_mode == "V2":
                    message_element = self.test.milestones.getElement([("name", "text_view", "=="), ("title_text", "OK", "==")], elements)
                    if message_element is not None:
                        self.test.log_assert(message_element,"Notification dismissal not found on notification: " + notification)
                        self.test.wait(3)
                        self.test.say('closing notification')
                        self.test.appium.tap_element(message_element)
                    else:
                        self.test.appium.back()
                else:
                    self.go_to_previous_screen()

    def get_notification_message(self, elements=None):
        message = None
        notification = self.get_notification(elements)
        if notification:
            message = notification['text_0']
        return message

    def verify_notification(self):
        self.verify_active()
        message = self.get_notification_message()
        self.test.log_assert(message, "Notification not displayed")

    def verify_notification_message(self, message):
        self.verify_active()
        notification = self.get_notification()
        self.test.log_assert(notification, "Cannot find notification")
        self.test.log_assert(message[:10] in notification['text_0'], "notification: %s does not include to: %s"%(notification['text_0'],message))

    def verify_dismiss(self, exists):
        elements = self.test.milestones.getElements()
        element = self.test.milestones.getElement([("title_text", "DISMISS", "==")], elements)
        if exists:
            self.test.log_assert(not element, "Displayed notification view is not a blocker error message. DISMISS button is displayed.")
        else:
            self.test.log_assert(element, "Displayed notification view is a blocker error message. DISMISS button is not displayed.")


    def verify_notification_message_by_key(self, key, type="error"):
        self.verify_active()
        notification = self.get_notification()
        dic_value_msg = self.test.milestones.get_dic_value_by_key(key,type)
        self.test.log_assert(notification, "No notification displayed, expected notification: " + dic_value_msg)
        dicWithoutDot = dic_value_msg[:-1] #for treatment of error number which is not in 
        self.test.log_assert( dicWithoutDot.upper() in notification['text_0'] or  dicWithoutDot in notification['text_0'], "notification: %s is not equal to: %s"%(notification['text_0'],dic_value_msg))

    def verify_notification_button_name_by_key(self, key, type = "general"):
        self.verify_active()
        notification = self.get_notification()
        dic_value_msg = self.test.milestones.get_dic_value_by_key(key, type)
        screenElements = self.test.milestones.getElements()
        button = self.test.milestones.getElement([("title_text", dic_value_msg.upper(), "==")], screenElements)
        if button is None:
            button = self.test.milestones.getElement([("title_text", dic_value_msg, "==")], screenElements)
        if 'button_0' in notification:
            notification_msg = notification['button_0']
        else:
            notification_msg = notification['text_0']
        self.test.log_assert(button, "notification: %s is not equal to: %s"%(notification_msg ,dic_value_msg))
        return button

    def get_notification_button_name_by_key(self, key, type = "general"):
        self.verify_active()
        dic_value_msg = self.test.milestones.get_dic_value_by_key(key, type)
        screenElements = self.test.milestones.getElements()
        button = self.test.milestones.getElement([("title_text", dic_value_msg.upper(), "==")], screenElements)
        if button is None:
            button = self.test.milestones.getElement([("title_text", dic_value_msg, "==")], screenElements)
        return button

    def tap_notification_button(self, key, type = "general"):
        button = self.verify_notification_button_name_by_key(key, type)
        self.test.wait(5)
        self.test.appium.tap_element(button)

    def get_and_tap_notification_button(self, key, type = "general"):
        button = self.get_notification_button_name_by_key(key, type)
        self.test.wait(5)
        self.test.appium.tap_element(button)

    def verify_entitlement_error_notification(self):
        current_screen = self.test.milestones.get_current_screen()
        if (current_screen == 'infolayer'):
            notification_message = self.test.screens.infolayer.verify_notification_message('DIC_ERROR_PLAYBACK_CONTENT_NOT_ENTITLED')
            self.test.appium.tap_element(notification_message)
        else:
            self.verify_notification_message_by_key('DIC_ERROR_PLAYBACK_CONTENT_NOT_ENTITLED')
            self.dismiss_notification()
