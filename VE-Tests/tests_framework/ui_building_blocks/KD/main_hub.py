__author__ = 'bwarshaw'

from time import sleep
from enum import Enum
from tests_framework.ui_building_blocks.screen import Screen
from tests_framework.ui_building_blocks.screen import ScreenDismiss
import logging
from operator import itemgetter
from tests_framework.ui_building_blocks.screen import ScreenActions
from tests_framework.ve_tests.tests_conf import DeviceType

''' Constants '''
TIMEOUT = 2
FOCUS_SHOWCASE_TIMEOUT = 4
MAIN_HUB_DISMISS_TIMEOUT = 15
NAVIGATE_TO_MAIN_HUB_TIMEOUT = 3
OPEN_VOD_ACTION_MENU_TIME_OUT = 2.5
RECOMMENDATION_LIMIT =9

class EventViewTypes(Enum):
    linear_event = "linear_event"
    library_event = "library_event"
    vod_event = "vod_event"


class EventViewPosition(Enum):
    left_event = "left_event"
    middle_event = "middle_event"
    right_event = "right_event"


class Showcases(Enum):
    STORE = "store"
    LIBRARY = "library"
    GUIDE = "guide"


class MainHub(Screen):
    ZOOM_PINCH_COUNT = 2
    MAIN_HUB_TOTAL_CHANNEL_COUNT = 9
    MAIN_HUB_CONTENT_EXPO_LEVELS_COUNT = 3

    def __init__(self, test):
        Screen.__init__(self, test, "main_hub")
        self.timeout = MAIN_HUB_DISMISS_TIMEOUT
        self.mainHubLayerData = None

        self.ctap_url = ""

    def navigate(self):
        logging.info("Navigate to main hub")
        elements = self.test.milestones.getElements()
        screen_name = self.test.milestones.get_current_screen(elements)

        if not screen_name:
            logging.info("the view does not contains screen name, navigation not performed")
            return

        if screen_name == "main_hub":
            return

        elif screen_name == "fullscreen":
            #KD- if there is no DATA in event, tap on fullscreen navigates to mainhub
            self.test.ui.center_tap()
            self.test.wait(2)
            current_screen = self.test.milestones.get_current_screen()
            if current_screen == "main_hub":
                return
            elif current_screen != "action_menu":
                self.test.screens.linear_action_menu.navigate()
            self.navigate()
            return

        elif screen_name == "infolayer":

            # Check for Pincode Screen for K, as Pincode screen in K is in InfoLayer
            if self.test.project.upper() != "KD":
                elements = self.test.milestones.getElements()
                unlock_program = self.test.milestones.get_dic_value_by_key("DIC_INFO_LAYER_UNLOCK_BUTTON").upper()
                unlock = self.test.milestones.getElement([("title_text",unlock_program , "==")], elements)
                if unlock:
                    self.tap_center_screen()
                    self.test.wait(TIMEOUT*2)
                    self.go_to_previous_screen()
            else:
                self.test.screens.infolayer.dismiss(action = self.test.screens.infolayer.dismissTypes.TAP)
                self.navigate()
                return

        elif screen_name == "pincode":
            self.go_to_previous_screen()
            current_screen = self.test.milestones.get_current_screen()
            self.test.log_assert(current_screen!='pincode', "pincode screen was not dismiss after moving to previous screen")
            self.navigate()
            return

        else:
            home_label = self.test.milestones.getElement([("title_text", "HOME", "==")], elements)
            self.test.log_assert(home_label, "No button to home page in milestone in current screen. screen = %s" % screen_name)
            self.test.appium.tap_element(home_label)

        self.verify_active()

    def focus_showcase(self, showcase):
        if showcase not in [Showcases.GUIDE, Showcases.LIBRARY, Showcases.STORE]:
            return
        elements = self.test.milestones.getElements()
        screen = self.test.milestones.get_current_screen(elements)
        if screen != "main_hub":
            return

        tv_showcase = self.test.milestones.getElement([("name", "ShowcaseExpo_GUIDE", "==")], elements)
        store_showcase = self.test.milestones.getElement([("name", "ShowcaseExpo_STORE", "==")], elements)
        library_showcase = self.test.milestones.getElement([("name", "ShowcaseExpo_LIBRARY", "==")], elements)
        showcase_str = None

        if showcase is Showcases.GUIDE:
            self.test.log_assert(tv_showcase, "Showcase for GUIDE was not found on screen")
            showcase_str = "GUIDE"
            if library_showcase["is_showcase_focused"]:
                self.test.appium.swipe_element(library_showcase, tv_showcase["width"], ScreenActions.LEFT)
            elif store_showcase["is_showcase_focused"]:
                self.test.appium.swipe_element(store_showcase, tv_showcase["width"], ScreenActions.RIGHT)
        if showcase is Showcases.LIBRARY:
            self.test.log_assert(library_showcase, "Showcase for LIBRARY was not found on screen")
            showcase_str = "LIBRARY"
            if tv_showcase["is_showcase_focused"]:
                self.test.appium.swipe_element(tv_showcase, tv_showcase["width"], ScreenActions.RIGHT)
            elif store_showcase["is_showcase_focused"]:
                self.test.appium.swipe_element(store_showcase, tv_showcase["width"], ScreenActions.RIGHT)
                self.test.appium.swipe_element(store_showcase, tv_showcase["width"], ScreenActions.RIGHT)

        if self.test.project.upper() == "K":
            if showcase == Showcases.STORE:
                self.test.log_assert(store_showcase, "Showcase for STORE was not found on screen")
                showcase_str = "STORE"
                #self.test.wait(5)
                if(self.test.milestones.get_current_screen() == "notification"):
                    self.test.screens.notification.go_to_previous_screen()
                if tv_showcase["is_showcase_focused"]:
                    self.test.appium.swipe_element(tv_showcase, tv_showcase["width"], ScreenActions.LEFT)
                    self.test.appium.swipe_element(library_showcase, library_showcase["width"], ScreenActions.LEFT)
                elif library_showcase["is_showcase_focused"]:
                    self.test.appium.swipe_element(library_showcase, tv_showcase["width"], ScreenActions.LEFT)

        else :
            if showcase == Showcases.STORE:
                self.test.log_assert(store_showcase, "Showcase for STORE was not found on screen")
                showcase_str = "STORE"
                #self.test.wait(5)
                if(self.test.milestones.get_current_screen() == "notification"):
                    self.test.screens.notification.go_to_previous_screen()
                if tv_showcase["is_showcase_focused"]:
                    self.test.appium.swipe_element(tv_showcase, tv_showcase["width"], ScreenActions.LEFT)
                    #self.test.appium.swipe_element(tv_showcase, tv_showcase["width"], ScreenActions.LEFT)
                elif library_showcase["is_showcase_focused"]:
                    self.test.appium.swipe_element(library_showcase, tv_showcase["width"], ScreenActions.LEFT)
                    self.test.appium.swipe_element(library_showcase, tv_showcase["width"], ScreenActions.LEFT)


        for i in range(FOCUS_SHOWCASE_TIMEOUT*2):
            self.test.wait(0.5)
            focused_showcase = self.test.milestones.getElement([("name", "ShowcaseExpo_"+showcase_str, "=="), ("is_showcase_focused", True, "==")])
            if focused_showcase:
                break
        if (not focused_showcase):
            return False
        return True
        #self.test.log_assert(focused_showcase, "No focused showcase in %s" %showcase_str)

    def get_showcase_by_type(self, showcase):
        showcase_widget = None
        if showcase not in [Showcases.GUIDE, Showcases.LIBRARY, Showcases.STORE]:
            return showcase_widget
        elements = self.test.milestones.getElements()
        screen = self.test.milestones.get_current_screen(elements)
        if screen != "main_hub":
            logging.warn("Not in main hub screen. screen=%s" % screen)
            return showcase_widget

        if showcase is Showcases.GUIDE:
            showcase_widget = self.test.milestones.getElement([("name", "ShowcaseExpo_GUIDE", "==")], elements)
        elif showcase is Showcases.STORE:
            showcase_widget = self.test.milestones.getElement([("name", "ShowcaseExpo_STORE", "==")], elements)
        elif showcase is Showcases.LIBRARY:
            showcase_widget = self.test.milestones.getElement([("name", "ShowcaseExpo_LIBRARY", "==")], elements)
        else:
            logging.warn("Unexpected showcase=" + str(showcase))

        return showcase_widget

    ''' The method assumes that the current screen is MainHub.'''
    def tap_background(self):
        window_width, window_height = self.test.milestones.getWindowSize()

        screen = self.test.milestones.get_current_screen()
        if screen != "main_hub":
            logging.warn("Not in main hub screen. screen=%s" % screen)
            return

        logging.info("Tapping main hub background")
        self.test.appium.tap(window_width / 2 , window_height / 4)

    def get_events_by_source(self, event_source):
        events = []
        elements = self.test.milestones.getElements()

        for element in elements:
            if "name" in element and element["name"] == "event_view" and "event_source" in element:
                if element["event_source"] == event_source:
                    events.append(element)

        events = sorted(events, key=itemgetter('x_pos'))
        self.test.log_assert(events, "Cannot find events by source: " + str(event_source))
        return events

    def get_events_by_type(self, event_type):
        events = []
        elements = self.test.milestones.getElements()
    
        for element in elements:
            if "name" in element and element["name"] == "event_view" and "event_type" in element:
                if (event_type == "EVENT_CONTENT_TYPE_STANDALONE" and element["event_source"] == "EVENT_SOURCE_TYPE_LINEAR" and element["event_type"] == event_type) or (event_type == "EVENT_TYPE_VOD_ASSET" and element["event_source"] == "EVENT_SOURCE_TYPE_VOD" and element["event_type"] == event_type):
                    events.append(element)

        events = sorted(events, key=itemgetter('x_pos'))
        self.test.log_assert(events, "Cannot find events by type: " + str(event_type))
        return events

    def play_vod_asset_by_position(self, position, verify_streaming=True):
        self.open_vod_action_menu_by_position(position)
        self.test.screens.vod_action_menu.play_asset(verify_streaming)

    def open_vod_action_menu_by_position(self, position, ShowCaseType="STORE"):

        if ShowCaseType == "LIBRARY":
            ShowCaseType = Showcases.LIBRARY
        else:
            ShowCaseType = Showcases.STORE

        self.navigate()

        is_focused = self.focus_showcase(ShowCaseType)
        while (not is_focused):
            self.navigate()
            is_focused = self.focus_showcase(ShowCaseType)

        device_type = self.test.device_type
        vod_events = self.test.screens.main_hub.get_events_by_source("EVENT_SOURCE_TYPE_VOD")
        if position is EventViewPosition.left_event:
            self.test.log_assert(len(vod_events) > 0, "VOD event is missing in MainHub at index 0 \n" + str(vod_events))
            position = 0
        elif position is EventViewPosition.middle_event:
            if device_type != DeviceType.TABLET:
                 self.test.log_assert(False, "No middle event in main hub on smartphone\n")
            else:
                self.test.log_assert(len(vod_events) > 1, "VOD event is missing in MainHub at index 1\n" + str(vod_events))
                position = 1
        elif position is EventViewPosition.right_event:
            if device_type != DeviceType.TABLET:
                self.test.log_assert(len(vod_events) > 1, "VOD event is missing in MainHub at index 2 \n" + str(vod_events))
                position = 1
            else:
                self.test.log_assert(len(vod_events) > 2, "VOD event is missing in MainHub at index 2 \n" + str(vod_events))
                position = 2

        self.test.log_assert(position >= 0 and position < len(vod_events), "postion  " + str(position) + " is more than the vod event count " + str(len(vod_events)))
        self.test.appium.tap_element(vod_events[position])
        self.test.wait(OPEN_VOD_ACTION_MENU_TIME_OUT)

    @property
    def get_element_on_screen(self):
        linear_events = self.get_events_by_source("EVENT_SOURCE_TYPE_LINEAR")
        for event in linear_events:
            if "title_text" in event:
                linear_event_with_title = event["title_text"]
                break
        self.test.log_assert(linear_event_with_title, "Cannot find events by source with title_text")
        return linear_event_with_title

    def get_current_channel(self):
        return self.get_element_on_screen

    def tune_to_linear_channel_by_position(self, position, verify_streaming=True):
        self.test.log_assert(position in [EventViewPosition.left_event, EventViewPosition.middle_event, EventViewPosition.right_event])
        self.navigate()

        device_type = self.test.device_type

        linear_events = self.get_events_by_source("EVENT_SOURCE_TYPE_LINEAR")

        self.test.log_assert(linear_events, "Cannot find linear events")
        self.test.log_assert(len(linear_events) > 0, "Empty linear events array")

        logging.info('linear events: %s', linear_events)
        if position is EventViewPosition.left_event:
            self.test.log_assert(len(linear_events) > 0, "Linear event is missing in MainHub at index 0 \n" +str(linear_events))
            position = 0
        elif position is EventViewPosition.middle_event:
            if device_type != DeviceType.TABLET:
                 self.test.log_assert(False, "No middle event in main hub on smartphone\n")
            else:
                self.test.log_assert(len(linear_events) > 1, "Linear event is missing in MainHub at index 1\n" + str(linear_events))
                position = 1
        elif position is EventViewPosition.right_event:
            if device_type != DeviceType.TABLET:
                self.test.log_assert(len(linear_events) > 1, "Linear event is missing in MainHub at index 2 \n" + str(linear_events))
                position = 1
            else:
                self.test.log_assert(len(linear_events) > 2, "Linear event is missing in MainHub at index 2 \n" + str(linear_events))
                position = 2

        if self.test.platform == "iOS":
            position -= len(linear_events)

        self.test.log_assert(linear_events and len(linear_events), "No Linear Events")
        try:
            self.test.appium.tap_element(linear_events[position])
        except IndexError:
            self.test.log_assert(False, "position " + str(position) + " not found in " + str(linear_events))

        if verify_streaming:
            self.test.screens.playback.verify_streaming_playing()
        return linear_events[position]

    "dismiss can occur by tap on video or after timeout"
    def dismiss(self, action = ScreenDismiss.TAP):
        self.test.log_assert(action in [ScreenDismiss.TAP, ScreenDismiss.TIMEOUT], "Unknown action  %s in dismiss main hub" % action)
        logging.info("Dismiss main hub by %s" % action.value)

        if action == ScreenDismiss.TAP:
            self.tap_background()

            # Check for Pincode Screen for K, as Pincode screen in K is coming as InfoLayer
            if self.test.project.upper() != "KD":
                self.test.wait(TIMEOUT)
                elements = self.test.milestones.getElements()
                unlock_program = self.test.milestones.get_dic_value_by_key("DIC_INFO_LAYER_UNLOCK").upper()
                unlock = self.test.milestones.getElement([("title_text",unlock_program , "==")], elements)
                if unlock:
                    self.test.screens.infolayer.verify_active()
            else:
                self.test.screens.fullscreen.verify_active()
        elif action == ScreenDismiss.TIMEOUT:
            for i in range(1, MAIN_HUB_DISMISS_TIMEOUT):
                sleep(1)
                screen = self.test.milestones.get_current_screen()
                if screen != 'main_hub':
                    break
            self.test.log_assert(screen!='main_hub', "Main hub does not dismiss after timeout (%d seconds)"%MAIN_HUB_DISMISS_TIMEOUT)
            self.test.log_assert(screen=='fullscreen', "Not switching to fullscreen after main hub dismiss. screen=%s"%screen)
            return i

    def get_showcase_in_focus(self):
        elements = self.test.milestones.getElements()
        tv_showcase_element = self.test.milestones.getElement([("name", "ShowcaseExpo_GUIDE", "==")], elements)
        store_showcase_element = self.test.milestones.getElement([("name", "ShowcaseExpo_STORE", "==")], elements)
        library_showcase_element = self.test.milestones.getElement([("name", "ShowcaseExpo_LIBRARY", "==")], elements)

        if tv_showcase_element["is_showcase_focused"]:
            return "ShowcaseExpo_GUIDE"

        if store_showcase_element["is_showcase_focused"]:
            return "ShowcaseExpo_STORE"

        if library_showcase_element["is_showcase_focused"]:
            return "ShowcaseExpo_LIBRARY"

    def pinch(self, showcase=None,percent=200, steps=50):
        if self.test.milestones.get_current_screen() != "main_hub":
            return

        if showcase in [Showcases.GUIDE, Showcases.LIBRARY, Showcases.STORE]:
            self.focus_showcase(showcase)

        current_showcase = self.get_showcase_in_focus()
        #self.test.appium.pinch(current_showcase, percent, steps)
        elements = self.test.milestones.getElements()
        showcase_element_scroller = self.test.milestones.getElement([("name",current_showcase, "==")], elements)
        self.test.appium.swipe_element(showcase_element_scroller, showcase_element_scroller["height"] / 1.5, ScreenActions.UP, 100)

    def zoom(self, showcase=None):
        if self.test.milestones.get_current_screen() != "main_hub":
            return

        if showcase in [Showcases.GUIDE, Showcases.LIBRARY, Showcases.STORE]:
            self.focus_showcase(showcase)
        current_showcase = self.get_showcase_in_focus()
        #self.test.appium.zoom(current_showcase)
        elements = self.test.milestones.getElements()
        showcase_element_scroller = self.test.milestones.getElement([("name",current_showcase, "==")], elements)
        self.test.appium.swipe_element(showcase_element_scroller, showcase_element_scroller["height"], ScreenActions.DOWN, 100)

    def getSnapshot(self):
        self.mainHubLayerData = self.test.milestones.getElements()

    def tap_centered_channel(self):
        element = self.test.milestones.getElementsArray([("name", "event_view", "==")],self.mainHubLayerData)
        self.test.appium.tap_element(element[-2])

    def verify_metadta(self):
        self.navigate()

        num_of_events = 0
        for i in range(self.ZOOM_PINCH_COUNT+1):
            ctap_grid_info =  self.test.ctap_data_provider.send_request('GRID', None)
            events = self.get_events_by_type("EVENT_CONTENT_TYPE_STANDALONE")
            for event in events:
                ctap_channel = self.test.ctap_data_provider.get_channel_info(event['channel_id'], ctap_grid_info)
                event_progress = float(event['progress_bar'])
                if  event_progress  > 0.1 and event_progress < 0.9:
                    self.test.ctap_data_provider.compare_event_metadata(event, ctap_channel)
                else:
                    logging.info("Event progress [%f] is close to event boundary, skip ctap compare" % event_progress)

            num_of_events = num_of_events + len(events)

            self.zoom(showcase=Showcases.GUIDE)

        self.test.log_assert(num_of_events == self.MAIN_HUB_TOTAL_CHANNEL_COUNT, "The channel count in Main hub should be %d, the count is %d" %(self.MAIN_HUB_TOTAL_CHANNEL_COUNT, num_of_events))

    def verify_vod_metadata(self, checkForErotic = False, ShowCaseType="STORE"):
        self.navigate()

        if ShowCaseType == "LIBRARY":
            ShowCaseType = Showcases.LIBRARY
        else:
            ShowCaseType = Showcases.STORE

        is_focused = self.focus_showcase(ShowCaseType)
        while (not is_focused):
            self.navigate()
            is_focused = self.focus_showcase(ShowCaseType)
        payload = {'isAdult':'false', 'limit': str(RECOMMENDATION_LIMIT), 'source':'vod'}
        #Get VOD recommendations from CTAP
        ctap_recommendation_info =  self.test.ctap_data_provider.send_request('RECOMMENDATIONS', payload)
        total_no_events = ctap_recommendation_info['count']
        event_index = 0
        zoom_count = 0
        logging.info("Start comparing events in forward direction")
        while event_index < total_no_events and zoom_count < (self.ZOOM_PINCH_COUNT+1):
            events = self.get_events_by_source("EVENT_SOURCE_TYPE_VOD")
            for event in events:
                ctap_recommendation_event = ctap_recommendation_info['content'][event_index]
                self.test.ctap_data_provider.compare_vod_event_metadata(event, ctap_recommendation_event)
                if checkForErotic :
                    self.test.log_assert(ctap_recommendation_event['content']['isErotic'] == False, "Erotic content is present. Content %s" %(ctap_recommendation_event))
                event_index = event_index+1
            self.zoom(showcase=ShowCaseType)
            zoom_count= zoom_count+1
            logging.info("Zoomed to next level")
        event_index = event_index-1
        logging.info("Start comparing events in reverse direction")
        # Pinch as many times as zoom was performed.
        while zoom_count > 0 and event_index >= 0:
            events = self.get_events_by_source("EVENT_SOURCE_TYPE_VOD")
            for event in reversed(events):
                self.test.ctap_data_provider.compare_vod_event_metadata(event, ctap_recommendation_info['content'][event_index])
                event_index = event_index-1

            self.pinch(showcase=ShowCaseType,percent=75)
            zoom_count = zoom_count-1
            logging.info("Pinch to previous level")

    def get_linear_recommended(self):
        elements = self.test.milestones.getElements()
        recommended = []

        for element in elements:
            if "event_source" in element and element["event_source"] == "EVENT_SOURCE_TYPE_LINEAR":
                recommended.append(element)

        return recommended

    def verify_linear_recommendation_metadata(self):
        self.navigate()
        sleep(1)

        is_focused = self.focus_showcase(Showcases.GUIDE)
        while (not is_focused):
            self.navigate()
            is_focused = self.focus_showcase(Showcases.GUIDE)
        sleep(1)
        events = []

        for i in range(self.ZOOM_PINCH_COUNT+1):
            events += self.get_linear_recommended()
            self.zoom(showcase=Showcases.GUIDE)

        # Remove progress_bar, as it will help duplication of same event
        # Removing duplicates from dict of array
        seen = set()
        unique_events = []
        for event in events:
            if "progress_bar" in event:
                event.pop("progress_bar")
            data = tuple(event.items())
            if data not in seen:
                seen.add(data)
                unique_events.append(event)

        unique_events = unique_events[1:]

        for event in unique_events:
            self.verify_linear_event_metadata(event)

    def verify_last_play_by_selection(self):
        test = self.test
        fullscreen = test.screens.fullscreen
        playback = test.screens.playback
        count = 0
        retry_attempts = 20

        self.verify_last_played_channel()
        fullscreen.navigate()
        sleep(4)

        playback_status = test.milestones.getPlaybackStatus()
        start_playing_channel = playback_status["currentChannelId"]
        fullscreen.swipe_channel(ScreenActions.DOWN)
        test.wait(8)
        playback_status = test.milestones.getPlaybackStatus()
        test.wait(2)
        while count <= retry_attempts and playback_status["playbackState"] != "PLAYING":
            fullscreen.swipe_channel(ScreenActions.DOWN)
            test.wait(8)
            test.screens.notification.dismiss_notification()
            playback_status = test.milestones.getPlaybackStatus()
            count += 1

        playback_status = test.milestones.getPlaybackStatus()
        test.log_assert(playback_status["currentChannelId"] != start_playing_channel,"No Playable channel found")

        self.verify_last_played_channel()

    def verify_last_played_channel(self):
        hhId = self.test.he_utils.get_default_credentials()[0]
        last_tuned = str(self.test.he_utils.get_last_tuned_channel_for_device(hhId, None))
        self.navigate()
        sleep(1)
        self.focus_showcase(Showcases.GUIDE)
        is_focused = self.focus_showcase(Showcases.GUIDE)
        while (not is_focused):
            self.navigate()
            is_focused = self.focus_showcase(Showcases.GUIDE)
        events = self.get_linear_recommended()
        self.test.log_assert(len(events) >= 1, "Not able to get any linear events from Mainhub")
        first_channel = str(events[0]["channel_id"])
        log_msg = "Last tuned is not correct.\n Last Channel in UPM: %s\n Last Channel in UI: %s" % (last_tuned, first_channel)
        self.test.log_assert(last_tuned == first_channel, log_msg)
        self.verify_current_event_with_ctap(events[0])

    # Gets the first event in UI's channel
    def get_first_event_channel(self):
        self.navigate()
        sleep(1)

        is_focused = self.focus_showcase(Showcases.GUIDE)
        while (not is_focused):
            self.navigate()
            is_focused = self.focus_showcase(Showcases.GUIDE)
        events = self.get_linear_recommended()
        self.test.log_assert(len(events) >= 1, "Not able to get any linear events from Mainhub")
        first_channel = str(events[0]["channel_id"])
        return first_channel

    def verify_current_event_with_ctap(self, first_event):
        test = self.test
        current_channel = first_event["channel_id"]
        ctap_event = test.ctap_data_provider.get_current_event_by_id(current_channel)
        test.log_assert(ctap_event, "Unable to find any CTAP data for last played channel\nCTAP: %s" % str(ctap_event))
        error_text = "First event is not the Tuned Event.\n CTAP Event: %s\n UI event: %s" \
                     % (str(ctap_event), str(first_event))

        start_time_str = ctap_event["startDateTime"]
        duration = ctap_event["duration"]
        ctap_time = test.ctap_data_provider.formatTimes(start_time_str, duration)

        test.log_assert(ctap_event["id"] == first_event["event_id"], error_text)
        test.log_assert(ctap_event["content"]["title"].upper() == first_event["title_text"].upper(), error_text)
        test.log_assert(ctap_time.upper() == first_event["time_text"].upper(), error_text)

    def get_recommended_content_instance(self, milestone_event, ctap_linear_recommended_info):
        event = None
        for content in ctap_linear_recommended_info:
            if milestone_event["event_id"] == content["id"]:
                event = content
                break
        return event

    def verify_linear_event_metadata(self, milestone_event):
        channel_id = milestone_event["channel_id"].strip()
        channel_data = self.test.ctap_data_provider.get_channel_info(channel_id)
        schedule = channel_data["schedule"]
        logging.info("CTAP Response: %s" %str(channel_data))
        self.test.log_assert(schedule, \
                             "No data found for channel(%s) in CTAP. \nCTAP Response %s" \
                             % (channel_id, str(channel_data)))

        ctap_event = self.get_ctap_event_by_id(milestone_event["event_id"], schedule)

        self.test.log_assert(ctap_event,\
                    "Unable to find event in CTAP Resp. \nUI Event: %s\n CTAP Resp: %s" \
                    %(str(milestone_event), str(channel_data)))

        start_time_str = ctap_event["startDateTime"]
        duration = ctap_event["duration"]
        ctap_time = self.test.ctap_data_provider.formatTimes(start_time_str, duration)

        self.test.log_assert(milestone_event["time_text"].upper() == ctap_time.upper(),\
                    "Time in UI is diff from CTAP. \nUI Event: %s\n CTAP Time: %s"\
                    %(str(milestone_event), str(ctap_time)))
        self.test.log_assert(ctap_event["content"]["title"].upper() in milestone_event["title_text"].upper(),\
                    "No match in title.\nTitle in UI: %s\n Title in CTAP: %s"\
                    %(milestone_event["title_text"], ctap_event["content"]["title"]))

    def get_ctap_event_by_id(self, event_id, schedule):
        ctap_event = None
        for event in schedule:
            if event["content"]["id"] == event_id:
                ctap_event = event
                break
        return ctap_event

    def check_erotic_content_linear(self):
        is_focused = self.focus_showcase(Showcases.GUIDE)
        while (not is_focused):
            is_focused = self.focus_showcase(Showcases.GUIDE)
        #there are be max of three zoom in
        for i in range(3):
            events = self.get_linear_recommended()
            for event in events:
                payload = {"event_id": event['event_id']}
                asset = self.test.ctap_data_provider.send_request('ACTION_MENU', payload)
                logging.info("Verifying asset: " + asset['content']['title'])
                self.test.log_assert(asset['content']['isErotic'] == False, "Erotic content is present. Content %s" %(asset))
            logging.info("Zoomed to next level")
            self.zoom(showcase=Showcases.GUIDE)

    def check_erotic_content_VOD(self):

        is_focused = self.focus_showcase(Showcases.STORE)
        while (not is_focused):
            is_focused = self.focus_showcase(Showcases.STORE)
        for i in range(3):
            events = self.get_events_by_source("EVENT_SOURCE_TYPE_VOD")

            for event in events:
                #remove ~VOD
                contentId = event['event_id'][:-4]
                asset = self.test.he_utils.vod_assets[contentId]
                logging.info("Verifying asset: " + asset['title'])
                self.test.log_assert(asset['isErotic'] == "false", "Erotic content is present. Content %s" %(asset))
            logging.info("Zoomed to next level")
            self.zoom(showcase=Showcases.STORE)


    def tune_to_channel_by_sek(self, channel_id, verify_streaming_started=True):
        element = self.scroll_to_channel_by_sek(channel_id)
        self.test.appium.tap_element(element)
        if verify_streaming_started:
            self.test.screens.playback.verify_streaming_playing()

    def scroll_to_channel_by_sek(self, channel_id):

        is_focused = self.focus_showcase(Showcases.GUIDE)
        while (not is_focused):
            is_focused = self.focus_showcase(Showcases.GUIDE)
        event = None
        for depth in range(self.ZOOM_PINCH_COUNT+1):
            event = self.test.milestones.getElement([("channel_id", str(channel_id), "=="), ("event_type", "linear_event", "==")])
            if event:
                break
            current_showcase = self.get_showcase_in_focus()
            #self.test.appium.zoom(current_showcase)

            self.test.appium.swipe_element(current_showcase, current_showcase["height"]/4, ScreenActions.UP)
            self.test.log("zooming in depth " + str(depth))
        self.test.log_assert(event, "Linear event with channel id: " + str(channel_id) + " not found")
        return event

    def tap_center_screen(self):
        window_width, window_height = self.test.milestones.getWindowSize()
        self.test.appium.tap(window_width / 2 , window_height / 2)

    def get_event_count(self):
        event_count = 2
        if self.test.device_type == "TABLET":
            event_count = 3
        return event_count * self.MAIN_HUB_CONTENT_EXPO_LEVELS_COUNT

