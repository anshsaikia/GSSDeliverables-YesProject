__author__ = 'hbonhomm'

from time import sleep
from operator import itemgetter
from tests_framework.ui_building_blocks.screen import Screen
from tests_framework.ui_building_blocks.screen import ScreenDismiss

import logging

''' Constants '''
OPEN_TIMELINE_FROM_FULLSCREEN_TIMEOUT = 4
TIMEOUT = 2
TIME_LINE_DISMISS_TIMEOUT = 15


class TimeLineCatchup(Screen):
    def __init__(self, test):
        Screen.__init__(self, test, "timeline_catchup")
        self.timeout = TIME_LINE_DISMISS_TIMEOUT
        self.maxChannelsToCycle = 500

    def navigate(self, swipe_direction=Screen.actionTypes.LEFT):
        logging.info("Navigate to timeline_catchup")
        screen = self.test.milestones.get_current_screen()
        if screen == "timeline_catchup":
            return

        if self.test.project != "KD" and self.test.app_mode == "V2":
            if screen != 'infolayer':
                self.test.say('need to navigate to info layer')
                self.test.screens.infolayer.show()
            self.test.ui.tap_center_element("timeline_catchup")
            self.test.wait(OPEN_TIMELINE_FROM_FULLSCREEN_TIMEOUT)
            self.verify_active()
            return

        self.test.screens.fullscreen.navigate()
        window_width, window_height = self.test.milestones.getWindowSize()
        y = window_height/2
        left_x = window_width*0.1
        right_x = window_width*0.75

        if swipe_direction == Screen.actionTypes.LEFT:
            self.test.appium.swipe_area(right_x, y, left_x, y)
        else:
            self.test.appium.swipe_area(left_x, y, right_x, y)

        self.test.wait(OPEN_TIMELINE_FROM_FULLSCREEN_TIMEOUT)

        self.verify_active()


    def find_channel_index_by_channelId(self, channelId, serverData):
        # Looking for index of channel
        index = 0
        channelIndex = -1
        for channel in serverData['channels']:
            if channel['id'] == channelId:
                channelIndex = index
                break
            index += 1
        self.test.log_assert(channelIndex != -1, "Can't find channel index")
        return channelIndex

    def find_next_channel_index(self, current_channel_index, server_data):
        if current_channel_index == server_data["count"] - 1:
            return 0
        else:
            return current_channel_index+1

    def find_prev_channel_index(self, current_channel_index, server_data):
        if current_channel_index == 0:
            return server_data["count"]-1
        else:
            return current_channel_index-1

    def find_next_channel_id(self, current_channel_id, server_data):
        current_channel_index = self.find_channel_index_by_channelId(current_channel_id, server_data)
        next_channel_index = self.find_next_channel_index(current_channel_index, server_data)
        return server_data["channels"][next_channel_index]["id"]

    def find_prev_channel_id(self, current_channel_id, server_data):
        current_channel_index = self.find_channel_index_by_channelId(current_channel_id, server_data)
        prev_channel_index = self.find_prev_channel_index(current_channel_index, server_data)
        return server_data["channels"][prev_channel_index]["id"]

    def find_catchup_event(self, elements = None):
        event_view = self.test.milestones.getElement([("event_source", "EVENT_SOURCE_TYPE_CATCHUP", "==")], elements)
        self.test.log_assert(event_view != None, "Can not find catchup event")
        return event_view

    def side_bar_tap(self):
        elements = self.test.milestones.getElements()
        up_arrow = self.test.milestones.getElement([("id", "upImageViewCatchup", "==")], elements)
        down_arrow = self.test.milestones.getElement([("id", "downImageViewCatchup", "==")], elements)
        window_width = self.test.milestones.get_value_by_key(elements, "window_width")
        self.test.log_assert(up_arrow, "Cannot find up arrow")
        self.test.log_assert(down_arrow, "Cannot find down arrow")
        top = (int(down_arrow['y_pos']) - int(up_arrow['y_pos'])) / 2
        left = (int(up_arrow['x_pos']) + int(up_arrow['width']) + int(window_width)) / 2

        element = {
            "name" : "left side bar tap",
            "x_pos": left,
            "y_pos": top,
            "width": 0,
            "height": 0
        }

        self.test.appium.tap_center_element(element)

    "dismiss can occur by tap on video or after timeout or after tap on exit button or after tap on more info button"
    def dismiss(self, action = ScreenDismiss.TAP):
        self.test.log_assert(action in [ScreenDismiss.TAP, ScreenDismiss.TIMEOUT, ScreenDismiss.CLOSE_BUTTON, ScreenDismiss.BACK_BUTTON, ScreenDismiss.TAP_ON_EVENT], "Unknown action  %s in dismiss timeline_catchup" % action)
        logging.info("Dismiss timeline_catchup by %s" % action.value)

        if action == ScreenDismiss.TAP:
            if self.test.project != "KD" and self.test.app_mode == "V2":
                self.side_bar_tap()
                self.test.screens.infolayer.verify_active()
                self.test.screens.infolayer.dismiss(action = self.test.screens.infolayer.dismissTypes.TAP)
            else:
                self.tap_background()
                self.test.screens.fullscreen.verify_active()
            return
        if action == ScreenDismiss.CLOSE_BUTTON:
            if self.test.project != "KD" and self.test.app_mode == "V2":
                self.test.ui.tap_element("exit")
                self.test.screens.infolayer.verify_active()
            return
        if action == ScreenDismiss.BACK_BUTTON:
            if self.test.project != "KD" and self.test.app_mode == "V2":
                self.test.ui.tap_element("back")
                self.test.screens.linear_action_menu.verify_active()
            return
        if action == ScreenDismiss.TAP_ON_EVENT:
            if self.test.project != "KD" and self.test.app_mode == "V2":
                event = self.test.milestones.getElement([("name", "event_view", "==")])
                self.test.appium.tap_element(event)
                self.test.screens.linear_action_menu.verify_active()
            return
        elif action == ScreenDismiss.TIMEOUT:
            for i in range(1, self.timeout):
                sleep(1)
                screen = self.test.milestones.get_current_screen()
                if screen != 'timeline_catchup':
                    break
            self.test.log_assert(screen!='timeline_catchup', "Timeline_catchup not dismiss after timeout (%d seconds)" % self.timeout)
            self.test.log_assert(screen=='fullscreen', "Not switching to fullscreen after timeline_catchup dismiss. screen=%s "% screen)
            return

    def tap_background(self):
        window_width, window_height = self.test.milestones.getWindowSize()

        screen = self.test.milestones.get_current_screen()
        if screen != "timeline_catchup":
            logging.warn("Not in timeline_catchup screen. screen=%s" % screen)
            return

        logging.info("Tapping timeline_catchup background")
        self.test.appium.tap(window_width / 2 , window_height / 3)

    def compare_events_metadata(self, server_data, elements, focused_channel_id, is_current):
        focused_channel_index = self.find_channel_index_by_channelId(focused_channel_id, server_data)
        last_event_index = len(server_data["channels"][focused_channel_index]["schedule"]) -1
        first_event_data = server_data["channels"][focused_channel_index]["schedule"][last_event_index]
        second_event_data = server_data["channels"][focused_channel_index]["schedule"][last_event_index-1]
        first_event_view = self.test.milestones.getElement([("event_id", first_event_data["id"], "==")], elements)
        second_event_view = self.test.milestones.getElement([("event_id", second_event_data["id"], "==")], elements)
        self.test.ctap_data_provider.compare_event_metadata(first_event_view, server_data["channels"][focused_channel_index], last_event_index, False, True)
        self.test.ctap_data_provider.compare_event_metadata(second_event_view, server_data["channels"][focused_channel_index], last_event_index-1, False, True)

    def compare_no_events_catchup(self, server_data, elements, focused_channel_id, is_current):
        focused_channel_index = self.find_channel_index_by_channelId(focused_channel_id, server_data)
        self.test.log_assert(len(server_data["channels"][focused_channel_index]["schedule"]) == 0, "ctap catchup event list for channel number(%d) is not empty"%focused_channel_index)
        event_view = self.test.milestones.getElement([("event_source", "EVENT_SOURCE_TYPE_CATCHUP", "==")], elements)
        self.test.log_assert(event_view == None, "Client catchup event list for channel number(%d) is not empty"%focused_channel_index)

    def compare_channels_logos(self, server_data, elements, focused_channel_id):
        focused_channel_index = self.find_channel_index_by_channelId(focused_channel_id, server_data)
        channels_panel = self.test.milestones.getElement([("name", "channels_panel", "==")], elements)
        channels_urls = [channels_panel["upper_channel_logo_url"], channels_panel["focused_channel_logo_url"], channels_panel["lower_channel_logo_url"]]
        upper_channel_index = self.find_prev_channel_index(focused_channel_index, server_data)
        lower_channel_index = self.find_next_channel_index(focused_channel_index, server_data)
        indexes = [upper_channel_index, focused_channel_index, lower_channel_index]
        j = 0
        for i in indexes:
            ctap_channel_logo = None
            for logo in server_data["channels"][i]['media']:
                if logo['type'] == "regular" and 'url' in logo:
                    ctap_channel_logo = logo['url']
            self.test.log_assert(channels_urls[j] == ctap_channel_logo, "Channel logo (%s) doesn't match ctap channel logo (%s)"%(channels_urls[j],ctap_channel_logo))
            j += 1
