__author__ = 'zhamilto'

from tests_framework.ui_building_blocks.screen import Screen, ScreenActions
from tests_framework.ve_tests.tests_conf import DeviceType
import logging

MAX_FOR_YOU_ASSETS = 10
MAX_ON_AIR_ASSETS = 10
MAX_FEATURE_POSTER_ASSETS = 4
OPEN_VOD_ACTION_MENU_TIME_OUT = 2.5

class TvFilter(Screen):
    def __init__(self, test):
        Screen.__init__(self, test, "tv_filter")

    def get_events_by_section(self, name):
        elements = self.test.milestones.getElements()
        events = self.test.ui.get_sorted_elements("event_view", 'x_pos', elements, "section", name)
        return events

    def wait_for_events_by_selection(self, name, events_must_exist=True):
        events = None
        for wait in range(0, 30):
            events = self.get_events_by_section(name)
            if events:
                break
            self.test.wait(1)

        if events_must_exist:
            self.test.log_assert(events, "Cannot find events for section " + name)

        return events


    def navigate(self):
        logging.info("Navigate to tv_filter")
        label_found = False
        for retry in range(0, 30):
            if self.test.screens.header.item_exists("DIC_MAIN_HUB_TV"):
                label_found = True
            # self.test.log_assert(not self.is_active(), "Television label not found but in tv-filter screen!")
            elements = self.test.milestones.getElements()
            screen_name = self.test.milestones.get_current_screen(elements)
            self.test.log("Currently in " + screen_name)
            if screen_name == "tv_filter":
                return
            if label_found:
                self.test.screens.header.tap_item("DIC_MAIN_HUB_TV")
            elif screen_name == "guide":
                self.test.ui.tap_element("back")
            elif screen_name == "action_menu" or screen_name == "trick_bar":
                self.test.ui.tap_element("exit")
                # When going back from action menu opened from search back might have "TELEVISION" label
                elements = self.test.milestones.getElements()
                screen_name = self.test.milestones.get_current_screen(elements)
                if screen_name == "tv_search":
                    if self.test.platform == "Android":
                        if self.test.device_type != DeviceType.TABLET:
                            self.test.ui.tap_localized_id("DIC_CANCEL")
                        else:
                            self.test.ui.tap_localized_label("DIC_CANCEL")
                    else:
                        self.test.ui.tap_localized_id("DIC_CANCEL")
                self.navigate()
            elif screen_name == "tv_search":
                if self.test.platform == "Android":
                    if self.test.device_type != DeviceType.TABLET:
                        self.test.ui.tap_localized_id("DIC_CANCEL")
                    else:
                        self.test.ui.tap_localized_label("DIC_CANCEL")
                else:
                    self.test.ui.tap_localized_id("DIC_CANCEL")
            elif screen_name == "full_content_screen":
                self.test.ui.tap_element("back")
            else:
                self.test.screens.infolayer.show()
                if self.test.device_type != DeviceType.TABLET and self.test.project != "KD":
                    self.test.ui.tap_element("exit")
                else:
                    self.test.ui.tap_element("actionmenu")
                    self.test.ui.tap_element("exit")
            self.test.wait(1)
        self.test.log_assert(label_found, "Cannot find television label")
        if not self.is_active():
            self.test.screens.header.tap_item("DIC_MAIN_HUB_TV")
        self.verify_active()

    def dismiss(self):
        self.verify_active()
        #Scroll down to reveal the on air events
        self.scroll_to_selection("DIC_FILTER_TV_ON_AIR")
        #Retrieve the poster events
        onAirTitle = self.test.milestones.get_dic_value_by_key("DIC_FILTER_TV_ON_AIR").upper()
        onAirEvents = self.wait_for_events_by_selection(onAirTitle)
        onAirFound = False
        for onAirEvent in onAirEvents:
            self.test.appium.tap_element(onAirEvent)
            #Wait for spinner to be removed
            self.test.ui.wait_for_element_removed("spinner")
            #Check if error message is not displayed
            elements = self.test.milestones.getElements()
            #Check for error
            if self.test.ui.element_exists("error_msg", elements):
                #Close notification
                self.test.screens.notification.dismiss()
                #Tap exit button
                self.test.ui.tap_element("exit", elements)
                self.verify_active()
            else:
                onAirFound = True
                break
        self.test.log_assert(onAirFound, "Cannot find poster in tv-filter that can be played")
        self.test.screens.infolayer.verify_active(ignoreNotification=True)
        from tests_framework.ui_building_blocks.screen import ScreenDismiss
        self.test.screens.infolayer.dismiss(ScreenDismiss.TAP)
        self.test.screens.fullscreen.verify_active(ignoreNotification=True)


    def count_events_each_sections(self):
        on_air_dic = self.test.milestones.get_dic_value_by_key("DIC_FILTER_TV_ON_AIR").upper()
        for_you_dic = self.test.milestones.get_dic_value_by_key("DIC_FILTER_FOR_YOU").upper()
        sections = {"poster": MAX_FEATURE_POSTER_ASSETS, on_air_dic: MAX_ON_AIR_ASSETS, for_you_dic: MAX_FOR_YOU_ASSETS}
        for i in range(0, len(sections)):
            self.test.wait(5)
            if self.get_events_by_section(sections.keys()[i]):
                channelsNumber = len(self.scroll_and_return_events(sections.keys()[i]))
                self.test.log_assert(channelsNumber <= sections.values()[i], "app present wrong number of events in:" + sections.keys()[i])


    def check_button_see_all(self):
        on_air_channels = self.test.ctap_data_provider.send_request("ON_AIR_LIST", None)
        if [on_air_channels["count"]] > 10:
            on_air_dic = self.test.milestones.get_dic_value_by_key("DIC_FILTER_TV_ON_AIR").upper()
            see_all_dic = self.test.milestones.get_dic_value_by_key("DIC_FILTER_SEE_ALL").upper()
            #Scroll down to reveal the on air events
            self.scroll_to_selection("DIC_FILTER_TV_ON_AIR")
            #Check elements
            elements = self.test.milestones.getElements()
            title_section = self.test.milestones.getElement(
                [("title_section", on_air_dic, "=="), ("title_text", see_all_dic, "==")], elements)
            self.test.log_assert(title_section, "See all button not found")

    def verify_first_item_after_tuned(self):
        feature_poster_event = self.test.milestones.getElement([("name", "event_view", "=="), ("section", "poster", "==")])
        self.test.appium.swipe_element(feature_poster_event, feature_poster_event["width"]+15, ScreenActions.LEFT, 2500)
        self.test.wait(2)
        tuned_channel = self.wait_for_events_by_selection("poster")[0]
        self.test.appium.tap_element(tuned_channel)
        self.test.screens.linear_action_menu.verify_active()
        self.test.screens.tv_filter.navigate()
        self.test.screens.tv_filter.verify_active()
        feature_poster_event = self.test.milestones.getElement([("name", "event_view", "=="), ("section", "poster", "==")])
        self.test.appium.swipe_element(feature_poster_event, feature_poster_event["width"], ScreenActions.RIGHT, 2500)
        self.test.wait(2)
        poster_first_item = self.wait_for_events_by_selection("poster")[0]
        self.test.log_assert('channel_number' in tuned_channel, "Cannot find channel number in tuned channel, item: [" + str(poster_first_item) + "] tuned channel: [" + str(tuned_channel) + "]")
        self.test.log_assert('channel_number' in poster_first_item, "Cannot find channel number in poster first item, item: [" + str(poster_first_item) + "] tuned channel: [" + str(tuned_channel) + "]")
        self.test.log_assert(poster_first_item['channel_number'] == tuned_channel['channel_number'],
                        "Not present last tuned channel on featured poster first items ")

    def scroll_and_return_events (self, section):
        channelsNumber = []
        new_event = ""
        sectionsEvents = self.wait_for_events_by_selection(section)
        self.test.log_assert('channel_number' in sectionsEvents[0], "Missing channel number in event: " + str(sectionsEvents[0]))
        last_event = sectionsEvents[0]['channel_number']
        while last_event != new_event:
            channelsNumber.append(sectionsEvents[0]['channel_number'])
            last_event = sectionsEvents[0]['channel_number']
            self.test.appium.swipe_element(sectionsEvents[0], sectionsEvents[0]["width"] + 15, ScreenActions.LEFT, 2500)
            self.test.wait(2)

            sectionsEvents = self.wait_for_events_by_selection(section)
            new_event = sectionsEvents[0]['channel_number']
        if len(sectionsEvents) > 1:
            for i in range(1, len(sectionsEvents)):
                channelsNumber.append(sectionsEvents[i]['channel_number'])

        item = len(sectionsEvents) - 1
        self.test.appium.swipe_element(sectionsEvents[item], (sectionsEvents[item]["width"] + 15 ) * len(channelsNumber), ScreenActions.RIGHT, 2500)
        self.test.wait(2)
        return channelsNumber

    def scroll_to_selection(self, dic_title):
        dic_title_text = self.test.milestones.get_dic_value_by_key(dic_title).upper()
        for scroll in range(0, 10):
            selection_label = self.test.ui.get_label_containing(dic_title_text)
            if selection_label:
                break
            self.test.ui.swipe_element("up")
        self.test.log_assert(selection_label, "Cannot find section " + dic_title)

    def verify_navigation_from_sections(self):
        on_air_dic = self.test.milestones.get_dic_value_by_key("DIC_FILTER_TV_ON_AIR").upper()
        for_you_dic = self.test.milestones.get_dic_value_by_key("DIC_FILTER_FOR_YOU").upper()
        feature_poster = self.wait_for_events_by_selection("poster")
        on_air_events = self.wait_for_events_by_selection(on_air_dic)
        for_you_events = self.wait_for_events_by_selection(for_you_dic, False) # it's OK if there aren't any events

        if feature_poster:
            self.test.log("Tapping event: " + str(feature_poster[0]))
            self.test.appium.tap_center_element(feature_poster[0])
            self.test.screens.linear_action_menu.verify_active()
            self.test.screens.tv_filter.navigate()
            self.test.screens.tv_filter.verify_active()

        if on_air_events:
            for evt in on_air_events:
                self.test.log("Tapping event: " + str(evt))
                self.test.appium.tap_center_element(evt)
                self.test.screens.infolayer.verify_active()
                self.test.screens.tv_filter.navigate()
                self.test.screens.tv_filter.verify_active()

        if for_you_events:
            for evt in for_you_events:
                self.test.log("Tapping event: " + str(evt))
                self.test.appium.tap_center_element(evt)
                self.test.screens.infolayer.verify_active()
                self.test.screens.tv_filter.navigate()
                self.test.screens.tv_filter.verify_active()


    def get_current_channel(self):
        self.navigate()
        #Scroll down to reveal the on air events
        self.scroll_to_selection("DIC_FILTER_TV_ON_AIR")
        onAirTitle = self.test.milestones.get_dic_value_by_key("DIC_FILTER_TV_ON_AIR").upper()
        result = self.wait_for_events_by_selection(onAirTitle)[0]["title_text"]
        self.test.log_assert(result , "No current channel in tv_filter , ON AIR section")
        return result

    def open_vod_action_menu_by_position(self, position):

        self.test.screens.store_filter.navigate()

        device_type = self.test.device_type
        vod_events = self.test.screens.main_hub.get_events_by_source("EVENT_SOURCE_TYPE_VOD")

        self.test.log_assert(position >= 0 and position < len(vod_events), "postion  " + str(position) + " is more than the vod event count " + str(len(vod_events)))
        self.test.appium.tap_element(vod_events[position])
        self.test.wait(OPEN_VOD_ACTION_MENU_TIME_OUT)





