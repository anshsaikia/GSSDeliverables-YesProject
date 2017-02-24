__author__ = 'upnidhi'

from time import sleep
from tests_framework.ui_building_blocks.screen import Screen
from tests_framework.he_utils.he_utils import VodContentType
from enum import Enum
import logging


'''Constants'''
TIMEOUT = 2

class YouthChanneltype(Enum):
    CURRENT_EVENT_PROTECTED = "current"
    ALL_EVENTS_PROTECTED = "all"
    ALTERNATELY_EVENTS_PROTECTED = "alternately"
    CURRENT_EVENT_LOW_RATED = "no"


class PinCodescreen(Screen):

    DISMISS_TIMEOUT_SEC = 60
    RETRY_COUNT = 3
    YOUTH_LIMIT_RATING = 16

    def __init__(self, test):
        Screen.__init__(self, test, "pincode")

    def navigate(self):
        logging.info("Navigate to pincode")
        elements = self.test.milestones.getElements()
        screen_name = self.test.milestones.get_current_screen(elements)

        if screen_name == self.screen_name:
            return

        if (screen_name == "infolayer") or (self.test.project == 'KD' and (screen_name == 'fullscreen' or screen_name == 'action_menu')):
            self.tap_unlock_program()

        elif screen_name == 'action_menu':
            self.test.screens.vod_action_menu.play_asset(verify_streaming=False, verify_fullscreen=False)

        else:
            logging.info('Cannot navigate to pincode directly')
            if self.test.project == 'KD':
                self.test.screens.main_hub.navigate()
            else:
                self.test.screens.tv_filter.navigate()
            self.test.wait(2)
            self.tune_to_locked_channel()
            self.test.wait(2)
            self.navigate()

        self.verify_active()

    def enter_pin(self, youthpin = None):
        self.verify_active()
        if youthpin == None:
            hh_id = self.test.configuration["he"]["generated_household"]
            if self.test.project != "KD":
                youthpin = self.test.he_utils.getParentalRatingPin(hh_id)
            else:
                youthpin = self.test.he_utils.getYouthpincode(hh_id)
        "Enter Pin"
        if self.test.platform == "Android" and self.test.app_mode != "V2":
            element = self.test.milestones.getElement([("name", "edit_text","==" )])
            self.test.log_assert(element)
            self.test.appium.tap_element(element)
            sleep(0.5)

        logging.info("Entering youth PIN %s" % youthpin)
        if self.test.project != "KD" and self.test.app_mode == "V2":
            elements = self.test.milestones.getElements()
            for digit in youthpin:
                element = self.test.milestones.getElement([("title_text", digit, "==")], elements)
                self.test.log_assert(element, "Key %s not found in milestone" % digit)
                self.test.appium.tap_element(element)
                self.test.wait(1)
        else:
            self.test.appium.type_keyboard(youthpin)

        sleep(TIMEOUT)

    def verify_message(self, message):
        self.verify_active()
        element = self.test.milestones.getElement([("title_text", message,"==" )])
        self.test.log_assert(element,"Message: '%s' Not shown on the screen" % message)

    def verify_pin_entry_disabled(self):
        pin_entry_enabled = self.test.milestones.getElement("pincode_entry_enabled")
        self.test.log_assert(pin_entry_enabled == False,"Pin entry not disabled")

    def get_youth_channel(self, type = YouthChanneltype.CURRENT_EVENT_PROTECTED):
        data = self.test.ctap_data_provider.send_request("GRID", None)
        self.test.log_assert(data["count"]!=0,"unable to retrieve data of grid")
        youth_channel = None
        for channel in data["channels"]:
            schedule = channel["schedule"]
            channel_id = channel ["id"]
            found = True
            if (type == YouthChanneltype.CURRENT_EVENT_PROTECTED):
                if "value" not in schedule[0]["content"]["parentalRating"]:
                    found = False
                else:
                    curr_event_pr = schedule[0]["content"]["parentalRating"]["value"]
                    if curr_event_pr < self.YOUTH_LIMIT_RATING:
                        found = False
            elif (type == YouthChanneltype.CURRENT_EVENT_LOW_RATED):
                if "value" not in schedule[0]["content"]["parentalRating"]:
                    found = False
                else:
                    curr_event_pr = schedule[0]["content"]["parentalRating"]["value"]
                    if curr_event_pr >= self.YOUTH_LIMIT_RATING:
                        found = False
            else:
                for i in range (len(schedule)-1):
                    if "value" not in schedule[i]["content"]["parentalRating"]:
                        continue;
                    event_pr = schedule[i]["content"]["parentalRating"]["value"]
                    next_event_pr = schedule[i+1]["content"]["parentalRating"]["value"]
                    if (type == YouthChanneltype.ALL_EVENTS_PROTECTED):
                        if event_pr < self.YOUTH_LIMIT_RATING:
                            found = False
                            break
                    elif (type == YouthChanneltype.ALTERNATELY_EVENTS_PROTECTED):
                         if((event_pr < self.YOUTH_LIMIT_RATING and next_event_pr < self.YOUTH_LIMIT_RATING) or (event_pr >= self.YOUTH_LIMIT_RATING and next_event_pr >= self.YOUTH_LIMIT_RATING)):
                            found = False
                            break

            if (found):
                youth_channel = channel_id
                break

        self.test.log_assert(youth_channel != None, "No youth protection channel (type=%s)" % type)
        return youth_channel

    def get_ctap_retry_count(self):
        pin_status = self.test.ctap_data_provider.send_request("PINCODE_STATUS", None)
        return pin_status['retriesLeft']

    def get_ctap_blocking_timeout(self):
        pin_status = self.test.ctap_data_provider.send_request("PINCODE_STATUS", None)
        self.test.log_assert(pin_status['isBlocked'] == True,"Pin status is Not blocked")
        return pin_status['timeLeft']

    def verify_subscreen(self, subscreen, timeout = 5):
        self.verify_active()
        client_subscreen=None
        for i in range (timeout):
            elements = self.test.milestones.getElements()
            client_subscreen = self.test.milestones.get_value_by_key(elements, "subscreen")
            if client_subscreen != subscreen:
                self.test.wait(1)
            else:
                return
        self.test.log_assert(client_subscreen == subscreen, "Failed to verify subscreen. expected subscreen = %s, actual subscreen = %s, timeout = %s" % (subscreen, client_subscreen, timeout))

    def get_expected_blocking_timeout_min(self):
        #TODO - change it to sec after ctap fix
        timeout_sec = self.get_ctap_blocking_timeout()
        timeout_min = timeout_sec / 60
        if (timeout_sec % 60 > 0):
            timeout_min = timeout_min + 1
        return timeout_min

    def get_client_blocking_timeout(self):
        self.verify_active()
        elements = self.test.milestones.getElements()
        blockingTimeout = self.test.milestones.get_value_by_key(elements, "blockingTimeout")
        self.test.log_assert(blockingTimeout, "No blockingTimeout in milstones")
        return blockingTimeout

    def is_youth_event(self, event):
         event_pr = event["content"]["parentalRating"]["value"]
         if event_pr >= self.YOUTH_LIMIT_RATING:
             return True
         return False

    def get_youth_asset(self):
        youth_asset = self.test.he_utils.getVodContent([VodContentType.SVOD, VodContentType.HIGH_RATED])
        self.test.log_assert(youth_asset != None, "No youth protection asset")
        return youth_asset

    def verify_pin_blocked(self):
        value_time_left = self.get_ctap_blocking_timeout()
        if int(value_time_left)/60 == 0:
            time_left = int(value_time_left)/60
        else:
            time_left = int(value_time_left)/60 + 1
        if self.test.project == "KD":
            pin_exhaust_msg = self.test.milestones.get_dic_value_by_key("DIC_PIN_CODE_LOCKED")
            pin_exhaust_msg %= str(time_left)
        else:
            pin_exhaust_msg = self.test.milestones.get_dic_value_by_key("DIC_PIN_CODE_INVALID_BLOCKED")
            pin_exhaust_msg = pin_exhaust_msg.replace("%1$s",str(time_left))

        element = self.test.milestones.getElement([('title_text', pin_exhaust_msg, '==')])
        return element is not None

    def navigate_to_low_rated_vod_asset(self):
        search = self.test.screens.search
        full_content = self.test.screens.full_content_screen
        asset = self.test.he_utils.getVodContent([VodContentType.SVOD, VodContentType.LOW_RATED, VodContentType.NON_EROTIC])

        logging.info("asset: {0}".format(asset))
        asset_title = asset['title']
        search.navigate()
        logging.info("searching for vod asset named {0}".format(asset_title))
        search.input_event_into_search_filed_and_search(asset_title)
        self.test.wait(4)
        if self.test.platform == "Android":
            search.navigate_to_action_menu_by_event_title(asset_title)
        else:
            full_content.tap_event_by_title(asset_title)

    def set_parental_rating_threshold(self, threshold=YOUTH_LIMIT_RATING):
        credentials = self.test.he_utils.get_default_credentials()
        self.test.he_utils.setParentalRatingThreshold(credentials[0], threshold)

    def navigate_to_locked_vod_asset(self):
        search = self.test.screens.search
        full_content = self.test.screens.full_content_screen
        pincode = self.test.screens.pincode

        high_rated_vod = pincode.get_youth_asset()

        logging.info("asset: {0}".format(high_rated_vod))
        asset_title = high_rated_vod['title']
        if self.test.project != "KD":
            self.test.screens.tv_filter.navigate()
            self.test.wait(3)
        search.navigate()
        self.test.wait(2)
        logging.info("searching for vod asset named {0}".format(asset_title))
        search.input_event_into_search_filed_and_search(asset_title)
        self.test.wait(2)
        if self.test.platform == "Android":
            search.navigate_to_action_menu_by_event_title(asset_title)
        else:
            full_content.tap_event_by_title(asset_title)
        self.test.wait(2)

    def tune_to_locked_channel(self, youth_channel_type = YouthChanneltype.CURRENT_EVENT_PROTECTED, verify_hidden=True):
        channel = self.get_youth_channel(youth_channel_type)
        if channel is None:
            logging.error("couldn't find channel with {0} high rated event/s".format(youth_channel_type))
            return None
        logging.info("found channel with {0} high rated event/s, channel id: {1}".format(youth_channel_type, channel))
        self.test.screens.zaplist.tune_to_channel_by_sek(channel, False)
        self.test.wait(3)
        if verify_hidden and not self.test.screens.playback.is_video_hidden():
            logging.error("video isn't hidden")
            return None
        logging.info("video is hidden as expected")
        return channel