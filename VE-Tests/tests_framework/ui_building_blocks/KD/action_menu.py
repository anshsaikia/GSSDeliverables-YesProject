__author__ = 'bwarshaw'

from tests_framework.ui_building_blocks.screen import Screen
from tests_framework.ui_building_blocks.screen import ScreenActions
from tests_framework.ve_tests.tests_conf import DeviceType
from tests_framework.ui_building_blocks.screen import ScreenDismiss
from enum import Enum
import calendar
import pytz.reference
import time
import logging
import math
import datetime

''' Constants '''
TIMEOUT = 2
DISMISS_ACTION_MENU_TIME_OUT = 2
MAX_RELATED_ASSETS = 10

class ButtonType_kd(Enum):
    RECORD = "DIC_ACTION_MENU_RECORD_BUTTON"
    STOP   = "DIC_ACTION_MENU_RECORD_STOP"
    DELETE = "DIC_ACTION_MENU_RECORD_DELETE"
    CANCEL = "DIC_ACTION_MENU_RECORD_CANCEL"
    PLAY   = "DIC_ACTION_MENU_PLAY_BUTTON"
    RESTART= "DIC_ACTION_MENU_RESTART_BUTTON"
    RESUME = "DIC_ACTION_MENU_RESUME_BUTTON"
    TRAILER = "DIC_ACTION_MENU_PLAY_TRAILER_BUTTON"
    LIVE_RESTART = "DIC_ACTION_MENU_LIVE_RESTART_BUTTON"

class ButtonConfirmationText_kd(Enum):
    STOP = "DIC_NOTIFICATION_RECORD_STOP_CONFIRMATION"
    DELETE = "DIC_NOTIFICATION_RECORD_DELETE_CONFIRMATION"
    CANCEL = "DIC_NOTIFICATION_RECORD_CANCEL_CONFIRMATION"


class ButtonType_k(Enum):
    RECORD = "DIC_ACTION_MENU_ACTION_RECORD"
    STOP   = "DIC_ACTION_MENU_ACTION_STOP_RECORDING"
    DELETE = "DIC_ACTION_MENU_ACTION_DELETE_RECORDING"
    CANCEL = "DIC_ACTION_MENU_ACTION_CANCEL_BOOKING"
    PLAY   = "DIC_ACTION_MENU_ACTION_PLAY"
    RESTART= "DIC_ACTION_MENU_ACTION_RESTART"
    RESUME = "DIC_ACTION_MENU_ACTION_RESUME"
    RENT   = "DIC_ACTION_MENU_ACTION_RENT"
    TRAILER = "DIC_ACTION_MENU_ACTION_TRAILER"
    MANAGE_RECORDINGS = "DIC_FILTER_LIBRARY_MANAGE_RECORDINGS"
    LIVE_RESTART = "DIC_ACTION_MENU_ACTION_RESTART_LIVE"

class ButtonConfirmationText_k(Enum):
    STOP = "DIC_RECORDING_STOP_CONFIRMATION"
    DELETE = "DIC_RECORDING_DELETE_CONFIRMATION"
    CANCEL = "DIC_NOTIFICATION_RECORD_CANCEL_CONFIRMATION"


class ActionMenu(Screen):
    def __init__(self, test):
        Screen.__init__(self, test, "action_menu")

        if self.test.project_type == "KD":
            self.button_type = ButtonType_kd
            self.button_confirmation_text = ButtonConfirmationText_kd
        else:
            self.button_type = ButtonType_k
            self.button_confirmation_text = ButtonConfirmationText_k

        self.event_type = "EVENT_CONTENT_TYPE_STANDALONE"

    def navigate(self):
        logging.info("Navigate to action menu")
        elements = self.test.milestones.getElements()
        screen = self.test.milestones.get_current_screen(elements)

        if screen == "action_menu":
            return
        if self.test.project != 'KD':
            self.test.screens.fullscreen.navigate()
            self.test.ui.top_tap()
            if self.test.device_type != DeviceType.TABLET:
                self.test.ui.tap_element("back")
            else:
                self.test.ui.tap_element("actionmenu")
            self.verify_active()
            return
        if self.test.autoPin and self.is_program_locked():
            self.tap_unlock_program()
            self.test.screens.pincode.enter_pin()
            self.test.screens.pincode.wait_untill_not_active()

        "Open action menu from fullscreen"
        self.test.screens.fullscreen.navigate()
        self.test.ui.center_tap()
        self.test.wait(2)
        self.verify_active()

    def navigate_from_timeline(self):
        time_line = self.test.screens.timeline
        time_line.navigate()
        time_line.dismiss(ScreenDismiss.TAP_ON_EVENT)
        self.test.screens.action_menu.verify_active()

    def navigate_from_catchup(self):
        catchup = self.test.screens.timeline_catchup
        catchup.navigate()
        catchup.dismiss(ScreenDismiss.TAP_ON_EVENT)
        self.test.screens.action_menu.verify_active()

    def navigate_from_vod(self):
        store = self.test.screens.store_filter
        store.navigate()
        store.tap_vod_asset_element()
        self.test.screens.action_menu.verify_active()

    def navigate_from_future_event(self):
        time_line = self.test.screens.timeline
        time_line.navigate()
        elements = self.test.milestones.getElements()
        future_event = self.test.milestones.getElements([("", "MORE INFO", "==")], elements)[1]
        self.test.log_assert(future_event, "Cannot find future event")
        self.test.appium.tap_element(future_event)
        self.test.screens.action_menu.verify_active()


    def dismiss(self):
        logging.info("Dismiss Action Menu")
        elements = self.test.milestones.getElements()
        if self.test.project != "KD" and self.test.app_mode == "V2":
            #self.test.ui.tap_element("fullscreen")
            self.test.ui.tap_element("exit")
        else:
            window_width, window_height = self.test.milestones.getWindowSize()
            action_menu_element = self.test.milestones.getElement([("name", "actions_menu", "==")])
            action_menu_top = action_menu_element["y_pos"]
            self.test.appium.tap(window_width/2, float(action_menu_top) - 5)
        self.test.wait(DISMISS_ACTION_MENU_TIME_OUT)
        current_screen = self.test.milestones.get_current_screen()
        if self.test.project == "KD":
            self.test.log_assert(current_screen == "fullscreen", "Failed dismiss Action Menu")
        else:
            self.test.log_assert(current_screen != "action_menu", "Failed dismiss Action Menu")

    def verify_data_with(self, lcn):
        serverData = self.test.ctap_data_provider.server_data_for_lcn(lcn)
        clientData = self.get_client_data()

        logging.info( "LCN = " + lcn)
        logging.info("%s <- S ?=? C -> " % (serverData["title"], (clientData["title"])))
        logging.info("%s <- S ?=? C -> " % (serverData["airingTime"], (clientData["airingTime"])))

        assert serverData["title"] != clientData["title"]
        assert serverData["airingTime"] != clientData["airingTime"]

    def compare_vod_sis_actionmenu_metadata(self):
        elements = self.test.milestones.getElements()
        event_id = self.test.ctap_data_provider.get_event_id(elements,type = "vod")
        server_data = self.test.ctap_data_provider.server_data_for_event_id(event_id)
        branding_info = self.test.milestones.get_element_by_key(elements, "background_image_url")
        print branding_info

        # if self.test.platform == "Android":
        #     branding_info =self.test.milestones.getElementContains(elements,"branding","id")
        # else:
        #     branding_info =self.test.milestones.getElementContains(elements,"actions_menu","name")
        self.test.ctap_data_provider.compare_background_image(branding_info, server_data)
        if self.test.platform == "Android":
            self.test.ctap_data_provider.compare_logo_bottom_image(branding_info, server_data)
        else:
            self.test.ctap_data_provider.compare_logo_bottom_image(self.test.milestones.getElementContains(elements,"event_view","name"), server_data)
        self.test.ctap_data_provider.compare_text_color(branding_info, server_data)

    def verify_vod_metadata_KV2(self, type="vod"):
        elements = self.test.milestones.getElements()
        event_id = self.test.ctap_data_provider.get_event_id(elements,type)
        server_data = self.test.ctap_data_provider.server_data_for_event_id(event_id)
        device_details = self.test.milestones.getDeviceDetails()

        '''Title'''
        self.test.log_assert(self.test.milestones.getElementContains(elements, server_data['content']["title"]),"No title on the screen")

        '''Synopsis'''
        synopsis = server_data['content']['synopsis']
        if "longSynopsis" in synopsis:
            self.test.log_assert( self.test.milestones.getElementContains(elements, synopsis["longSynopsis"]), "No longSynopsis on the screen")
        elif "shortSynopsis" in synopsis:
            self.test.log_assert(self.test.milestones.getElementContains(elements, synopsis["shortSynopsis"]),"No shortSynopsis & longSynopsis on the screen")

        '''Directors'''
        directors = self.test.ctap_data_provider.get_credits_from_content(server_data, 'content', 'DIRECTOR')
        for director in directors:
            self.test.log_assert(self.test.milestones.getElementContains(elements, director),"No Director: {0} on the screen".format(director))

        '''Actors'''
        actors = self.test.ctap_data_provider.get_credits_from_content(server_data, 'content', 'ACTOR')
        if len(actors)>4:
            actors = actors[0:4]
        for actor in actors:
            self.test.log_assert(self.test.milestones.getElementContains(elements, actor),"No Actor: {0} on the screen".format(actor))

        '''Year'''
        productionYear = str(server_data['content']['productionYear'])
        self.test.log_assert(self.test.milestones.getElementContains(elements, productionYear), "No productionYear present on the screen")

        '''Genres'''
        if "genres" in server_data['content']:
            genres = server_data['content']["genres"]
            if len(genres)>4:
                genres = genres[0:4]
            for genre in genres:
                self.test.log_assert(self.test.milestones.getElementContains(elements, genre['name']),"No Genre: {0} on the screen".format(genre['name']))

        '''Parental Rating'''
        parentalRating = str(server_data['content']['parentalRating']['value'])
        self.test.log_assert(self.test.milestones.getElementContains(elements, parentalRating), "No parentalRating present on the screen")

        '''Duration'''
        duration = str(int(server_data['content']['duration']) / 60000)
        self.test.log_assert(self.test.milestones.getElementContains(elements, duration), "No duration present on the screen")

        '''Video Quality'''
        videoFormat = server_data['content']['videoFormat']
        self.test.log_assert(self.test.milestones.getElementContains(elements, videoFormat), "No videoFormat present on the screen")

        '''Audio Quality'''
        audioFormat = server_data['content']['audioFormat']
        self.test.log_assert(self.test.milestones.getElementContains(elements, audioFormat), "No audioFormat present on the screen")

        '''Play Icon'''
        self.test.log_assert(self.test.milestones.getAnyElement([("id", "play", "==")], elements), "No play icon on the screen")

    def verify_linear_metadata_KV2(self):
        elements = self.test.milestones.getElements()
        event_id = self.test.ctap_data_provider.get_event_id(elements)
        server_data = self.test.ctap_data_provider.server_data_for_event_id(event_id)
        device_details = self.test.milestones.getDeviceDetails()

        '''Logo'''
        logos = server_data['channel']['media']
        for logo in logos:
            if logo['type'] == 'regular':
                logoUrl = logo['url']
                break
        channel_logo = self.test.milestones.getElement([("logoUrl", logoUrl, "==")], elements)
        self.test.log_assert(channel_logo, "No Logo present on the screen")

        '''Title'''
        self.test.log_assert(self.test.milestones.getElementContains(elements, server_data['content']["title"]),"No title on the screen")

        '''Airtime'''
        self.test.log_assert("duration" in server_data['content'], "No duration section in server data")
        start_time_utc = int(calendar.timegm(time.strptime(server_data['startDateTime'], "%Y-%m-%dT%H:%M:%S.%fZ"))) * 1000
        start_time_local = datetime.datetime.fromtimestamp(start_time_utc / 1000, pytz.timezone(device_details['timezone']))
        timeStrStart = start_time_local.strftime('%-I:%M')
        self.test.log_assert(self.test.milestones.getElementContains(elements, timeStrStart),"No start time on the screen")
        end_time_utc = start_time_utc + server_data['content']['duration']
        end_time_local = datetime.datetime.fromtimestamp(end_time_utc / 1000, pytz.timezone(device_details['timezone']))
        timeStrEnd = end_time_local.strftime('%-I:%M')
        self.test.log_assert(self.test.milestones.getElementContains(elements, timeStrEnd),"No end time on the screen")

        '''Synopsis'''
        synopsis = server_data['content']['synopsis']
        if "longSynopsis" in synopsis:
            self.test.log_assert( self.test.milestones.getElementContains(elements, synopsis["longSynopsis"]), "No longSynopsis on the screen")
        elif "shortSynopsis" in synopsis:
            self.test.log_assert(self.test.milestones.getElementContains(elements, synopsis["shortSynopsis"]),"No shortSynopsis & longSynopsis on the screen")

        '''Directors'''
        directors = self.test.ctap_data_provider.get_credits_from_content(server_data, 'content', 'DIRECTOR')
        for director in directors:
            self.test.log_assert(self.test.milestones.getElementContains(elements, director),"No Director: {0} on the screen".format(director))

        '''Actors'''
        actors = self.test.ctap_data_provider.get_credits_from_content(server_data, 'content', 'ACTOR')
        if len(actors)>4:
            actors = actors[0:4]
        for actor in actors:
            self.test.log_assert(self.test.milestones.getElementContains(elements, actor),"No Actor: {0} on the screen".format(actor))

        '''Year'''
        productionYear = str(server_data['content']['productionYear'])
        self.test.log_assert(self.test.milestones.getElementContains(elements, productionYear), "No productionYear present on the screen")

        '''Genres'''
        if "genres" in server_data['content']:
            genres = server_data['content']["genres"]
            if len(genres)>4:
                genres = genres[0:4]
            for genre in genres:
                self.test.log_assert(self.test.milestones.getElementContains(elements, genre['name']),"No Genre: {0} on the screen".format(genre['name']))

        '''Parental Rating'''
        parentalRating = str(server_data['content']['parentalRating']['value'])
        self.test.log_assert(self.test.milestones.getElementContains(elements, parentalRating), "No parentalRating present on the screen")

        '''Duration'''
        duration = str(int(server_data['content']['duration']) / 60000)
        self.test.log_assert(self.test.milestones.getElementContains(elements, duration), "No duration present on the screen")

        '''Video Quality'''
        videoFormat = server_data['content']['videoFormat']
        self.test.log_assert(self.test.milestones.getElementContains(elements, videoFormat), "No videoFormat present on the screen")

        '''Audio Quality'''
        audioFormat = server_data['content']['audioFormat']
        self.test.log_assert(self.test.milestones.getElementContains(elements, audioFormat), "No audioFormat present on the screen")

        '''check pip or play only if current event'''
        localTime = self.test.milestones.getLocalTime()
        self.test.log("localTime: " + str(localTime) + " start_time_local: " + str(start_time_local) + " end_time_local: " + str(end_time_local))
        if localTime > start_time_local and localTime < end_time_local:
            play_icon = self.test.milestones.getElement([("id", "play", "==")], elements)
            if not play_icon:
                '''PIP'''
                self.test.log_assert(self.test.milestones.getElement([("name", "pip_view", "==")], elements), "No PIP on the screen")

    def verify_metadata(self):
        elements = self.test.milestones.getElements()
        event_id = self.test.ctap_data_provider.get_event_id(elements)
        server_data = self.test.ctap_data_provider.server_data_for_event_id(event_id)
        device_details = self.test.milestones.getDeviceDetails()

        #self.compare_vod_sis_actionmenu_metadata(elements, server_data)

        #Action details -- assert only if content appears in server data but not in app
        synopsis = server_data['content']['synopsis']
        #self.test.log_assert( "longSynopsis" in synopsis, "No longSynopsis section in server data")
        if "longSynopsis" in synopsis:
            self.test.log_assert( self.test.milestones.getElementContains(elements, synopsis["longSynopsis"]), "No longSynopsis on the screen")

        directors = self.test.ctap_data_provider.get_credits_from_content(server_data, 'content', 'DIRECTOR')
        for director in directors:
            self.test.log_assert( self.test.milestones.getElementContains(elements, director), "No Director: {0} on the screen".format(director))

        actors = self.test.ctap_data_provider.get_credits_from_content(server_data, 'content', 'ACTOR')
        for actor in actors:
            self.test.log_assert( self.test.milestones.getElementContains(elements, actor), "No Actor: {0} on the screen".format(actor))

        #self.test.log_assert( "genres" in server_data['content'], "No genres section in server data")
        if "genres" in server_data['content']:
            for genre in server_data['content']["genres"]:
                self.test.log_assert( self.test.milestones.getElementContains(elements, genre['name']), "No Genre: {0} on the screen".format(genre['name']))

        self.test.log_assert( self.test.milestones.getElementContains(elements, server_data['content']["title"]), "No title on the screen")
        if "productionLocation" in server_data['content']:
            self.test.log_assert( self.test.milestones.getElementContains(elements, server_data['content']["productionLocation"]), "No productionLocation on the screen")

        self.test.log_assert( "duration" in server_data['content'], "No duration section in server data")
        duration_ms = int(server_data['content']["duration"])
        duration = str(duration_ms / 60000)
        start_time_utc = int(calendar.timegm(time.strptime(server_data['startDateTime'], "%Y-%m-%dT%H:%M:%S.%fZ"))) * 1000
        start_time_local = datetime.fromtimestamp(start_time_utc/1000, pytz.timezone(device_details['timezone']))

        end_time_utc = start_time_utc + server_data['content']['duration']
        end_time_local = datetime.fromtimestamp(end_time_utc/1000, pytz.timezone(device_details['timezone']))
        timeStrEN = "{} to {}".format(start_time_local.strftime('%H.%M') , end_time_local.strftime('%H.%M') )
        timeStrDE = "{} bis {}".format(start_time_local.strftime('%H.%M') , end_time_local.strftime('%H.%M') )

        self.test.log_assert( self.test.milestones.getElementContains(elements, duration) or self.test.milestones.getElementContains(elements, timeStrEN) or self.test.milestones.getElementContains(elements, timeStrDE), "No airtime found on the screen: \r\n"+ str(elements))


    def verify_pip_KV2(self):
        elements = self.test.milestones.getElements()
        self.test.log_assert(self.test.milestones.getElement([("name", "pip_view", "==")], elements), "No PIP on the screen")

    def verify_poster_KV2(self):
        elements = self.test.milestones.getElements()
        self.test.log_assert(self.test.milestones.getElement([("name", "poster", "==")], elements), "No POSTER on the screen")

    def verify_play_icon_KV2(self):
        elements = self.test.milestones.getElements()
        self.test.log_assert(self.test.milestones.getElement([("id", "play", "==")], elements),
                             "No POSTER on the screen")

    def chack_pip_or_poster_kv2(self):
        self.navigate()
        self.verify_pip_KV2()

        self.navigate_from_timeline()
        self.verify_pip_KV2()
        self.verify_play_icon_KV2()

        self.navigate_from_future_event()
        self.verify_poster_KV2()

    def verify_data(self):

        elements = self.test.milestones.getElements()
        if self.test.project != "KD" and self.test.app_mode == "V2":
            if self.test.milestones.getElementContains(elements, "EVENT_SOURCE_TYPE_VOD", "event_source"):
                self.verify_vod_metadata_KV2()
            elif self.test.milestones.getElementContains(elements, "EVENT_SOURCE_TYPE_CATCHUP", "event_source"):
                self.verify_vod_metadata_KV2("catchup")
            else:
                self.verify_linear_metadata_KV2()
        return

        if self.test.platform == "Android":
            #in Android the milestones goes by title_text in IOS by actors, directors and so on so we leave the different paths for this test
            self.verify_metadata()
            return

        event_id = self.test.ctap_data_provider.get_event_id(elements)
        server_data = self.test.ctap_data_provider.server_data_for_event_id(event_id)

        directors = self.test.ctap_data_provider.get_credits_from_content(server_data, 'content', 'DIRECTOR')
        actors = self.test.ctap_data_provider.get_credits_from_content(server_data, 'content', 'ACTOR')
        server_data['directors'] = directors
        server_data['actors'] = actors

        map_server_milestones = {"actors" : "actors",
                                  # "audioLanguages" : "",
                                  "directors" : "directors",
                                  "duration" : "durationYearLocation",
                                  "genres" : "genre",
                                  "synopsis" : "longSynopsis",
                                  "parentalRating" : "parentalRating",
                                  "productionLocation" : "durationYearLocation",
                                  "releaseYear" : "durationYearLocation"
                                  # "resource" : "",
                                  # "shortSynopsis" : "",
                                  # "subtitleLanguages" : "",
                                  # "thumbnails" : "",
                                  # "title" : "",
                                  # "type" : ""
                                  }

        for key in server_data.keys():
            server_item_value = server_data[key]
            if key in map_server_milestones:
                item_value_milestones = map_server_milestones[key]
            else:
                continue

            if not item_value_milestones:
                continue

            current_element_value = self.test.milestones.get_value_by_key(elements, item_value_milestones )
            if(not current_element_value):
                logging.info("Cannot find " + item_value_milestones + " in " + str(elements))
            if not isinstance(server_item_value , list):
               server_item_value = [server_item_value]

            #iterate over server lists
            for current_server_item_value in server_item_value:
                # print current_server_item_value

                if key == 'duration':
                    duration_ms = int(current_server_item_value)
                    duration = duration_ms /60000
                    current_server_item_value = str(duration)
                if key == 'parentalRating':
                    current_server_item_value = current_server_item_value['name']
                if key == 'synopsis':
                    current_server_item_value = current_server_item_value['longSynopsis']

                current_server_item_value = str(current_server_item_value)

                logging.info (current_server_item_value + " <- S ? = ? C-> " + current_element_value)
                self.test.log_assert(current_server_item_value in current_element_value, "Test Fail - server data is different from client data")

    def get_client_data(self):
        elements = self.test.milestones.getElements()
        creator_title = self.test.milestones.getElement("Creator: ", elements)
        creator_value_element = self.test.milestones.getElement([("y_pos", creator_title["y_pos"], "==") , ("x_pos", creator_title["x_pos"], ">")], elements)
        creator_value = creator_value_element["title_text"]
        logging.info(creator_value)


    def get_channel_id (self):
        elements = self.test.milestones.getElements()
        linear_event = self.get_linear_event(elements)
        self.test.log_assert(linear_event, "Cannot find element for '" + str(self.event_type) + "'")
        channel_id = linear_event["channel_id"]
        return channel_id

    def compare_playing_channel_id(self):
        playbackStatusInfo = self.test.milestones.getPlaybackStatus()
        current_playing_channel = playbackStatusInfo["currentChannelId"]
        action_menu_channel_id = self.get_channel_id()
        self.test.log_assert(current_playing_channel == action_menu_channel_id, "The action menu channel id " + str(action_menu_channel_id) + " is not the playing channel id " + str(current_playing_channel))

    def reveal_full_action_menu(self):
        window_width, window_height = self.test.milestones.getWindowSize()
        action_menu_element = self.test.milestones.getElement([("name", "actions_menu", "==")])
        self.test.appium.scroll_from_element(action_menu_element, window_width / 4, ScreenActions.UP)
        self.test.appium.scroll_from_element(action_menu_element, window_width / 4, ScreenActions.UP)
        self.verify_action_menu_revealed()

    def verify_action_menu_revealed(self, elements=None):
        if (elements == None):
            elements = self.test.milestones.getElements()
        window_width, window_height = self.test.milestones.getWindowSize()
        if self.test.platform == "iOS":
            linear_event = self.get_linear_event(elements)
            self.test.log_assert(linear_event['y_pos'] < window_height / 2, "full action menu is not revealed")
        else:
            action_menu = self.test.milestones.getElement([("event_type", "EVENT_CONTENT_TYPE_EPISODE", "==")], elements)
            related_menu = self.test.milestones.getElement([("event_type", "EVENT_CONTENT_TYPE_STANDALONE", "==")], elements)
            self.test.log_assert(related_menu['y_pos'] > action_menu['y_pos'] and related_menu['is_current'] != action_menu['is_current'], "full action menu is not revealed")

    def verify_action_menu_collapsed(self, elements=None):
        if(elements == None):
            elements = self.test.milestones.getElements()
        window_width, window_height = self.test.milestones.getWindowSize()
        if self.test.platform == "iOS":
            linear_event = self.test.milestones.getElement([("event_type", self.event_type, "==")], elements)
            self.test.log_assert(linear_event['y_pos'] > window_height / 4,"full action menu is not revealed")
        else:
            trick_mode = self.test.milestones.getElement([("name","trickmode_bar", "==")], elements)
            related_label = self.test.milestones.getElement([("title_text","RELATED", "==")], elements)
            self.test.log_assert( trick_mode['y_pos'] - (related_label['y_pos'] + related_label['height']) <= window_height / 100 * 5,"full action menu is not collapsed")

    def scroll_related_section(self):
        elements = self.test.milestones.getElements()
        if self.test.platform == "Android":
            events_scroller = self.test.milestones.getElement([("id", "related_items_scroll_area", "==")], elements)
        else:
            events_scroller = self.test.milestones.getElement([("id", "FullContentScroller", "==")], elements)

        related_elements = self.test.milestones.getElementInBorders(elements, events_scroller)
        if self.test.platform == "Android":
            related_elements.pop(0)
        related_num = len(related_elements)
        if related_num > 3:
            window_width, window_height = self.test.milestones.getWindowSize()
            self.test.appium.swipe_element(events_scroller, window_width / 5, ScreenActions.LEFT)
            # TODO: verification
            elements = self.test.milestones.getElements()
            self.test.log_assert(related_elements != self.test.milestones.getElementInBorders(elements, events_scroller), "Related scroller doesn't scroll")
        else:
            logging.info("This is only one page with related events, no need to scroll")

    def get_all_ltv_related_elements(self):
        relatedAssetsIdList = list()
        related_elements = list()
        relassetnb = 0
        store = self.test.screens.store
        relscreenelements = self.test.milestones.getElements()
        if self.test.platform == "Android":
            self.test.screens.action_menu.navigate()
            self.test.wait(2)
            self.test.screens.action_menu.reveal_full_action_menu()
            relscreenelements = self.test.milestones.getElements()
            logging.info("relscreenelements : %s" % (relscreenelements))
            events_scroller = self.test.milestones.getElement([("id","related_items_scroll_area", "==")], relscreenelements)
            logging.info("events_scroller : %s" % (events_scroller))
        elif self.test.platform == "iOS":
            self.test.wait(2)
            self.test.screens.action_menu.reveal_full_action_menu()
            relscreenelements = self.test.milestones.getElements()
            logging.info("relscreenelements : %s" % (relscreenelements))
            events_scroller = self.test.milestones.getElement([("id","FullContentScroller", "==")], relscreenelements)
        else:
            self.test.log_assert(self.test.platform == "Android" or self.test.platform == "iOS", "PLATFORM NOT SUPPORTED")
        relatedAssetsIdList = self.test.milestones.getElementInBorders(relscreenelements, events_scroller)
        if self.test.platform == "Android":
            relatedAssetsIdList.pop(0)
            relassetnb = len(relatedAssetsIdList)
        #logging.info("relatedAssetsIdList from getElementborder : %s" % relatedAssetsIdList)
        elements = list()
        #while related_elements != self.test.milestones.getElementInBorders(elements, events_scroller):
        while elements != self.test.milestones.getElements():
            elements = self.test.milestones.getElements()
            related_elements = self.test.milestones.getElementInBorders(elements, events_scroller)
            #related_elements = self.test.milestones.getElements()
            if self.test.platform == "Android" and len(relatedAssetsIdList)==relassetnb:
                related_elements.pop(0)
            #logging.info("related_elements : %s" % related_elements)
            for ltvasset in related_elements:
                #logging.info("ltvasset : %s" % ltvasset)
                ltveventid = ltvasset["event_id"]
                assetinlist = False
                for ltv_asset in relatedAssetsIdList:
                    ltv_eventid = ltv_asset["event_id"]
                    if str(ltveventid) == str(ltv_eventid):
                        assetinlist = True
                        break
                if not assetinlist:
                    relatedAssetsIdList.append(ltvasset)
            window_width, window_height = self.test.milestones.getWindowSize()
            self.test.appium.swipe_element(events_scroller, window_width / 5, ScreenActions.LEFT)
            #elements = self.test.milestones.getElements()
        return relatedAssetsIdList

    def tap_related_content(self):
        elements = self.test.milestones.getElements()
        if self.test.platform == "Android":
            events_scroller = self.test.milestones.getElement([("id", "related_items_scroll_area", "==")], elements)
        else:
            events_scroller = self.test.milestones.getElement([("id", "FullContentScroller", "==")], elements)

        related_elements = self.test.milestones.getElementInBorders(elements, events_scroller)
        if self.test.platform == "Android":
            related_elements.pop(0)
        self.test.appium.tap_element(related_elements[0])

        self.test.wait(2)
        elements_in_second_page = self.test.milestones.getElements()
        if self.test.platform == "Android":
            events_scroller_in_second_page = self.test.milestones.getElement([("id", "related_items_scroll_area", "==")], elements_in_second_page)
        else:
            events_scroller_in_second_page = self.test.milestones.getElement([("id", "FullContentScroller", "==")], elements_in_second_page)
        self.test.log_assert(not events_scroller_in_second_page, "Related are present in the second page")

    # this works for linear, although may need some improvement for scrolling, once there are enough related events.
    # this may need to be generalized or changed for vod.
    def examine_related_elements(self):
        related_dic = self.test.milestones.get_dic_value_by_key("DIC_FILTER_ACTION_MENU_RELATED").upper()
        self.test.wait(1)
        elements = self.test.milestones.getElements()
        # items can be linear events or vod assets
        items = self.test.ui.get_sorted_elements("event_view", "x_pos", elements, "section", related_dic)
        if not items:
            logging.error("No related items!")
        else:
            # first, scroll and verify count
            related_number = []
            last_item = items[0]['event_id']
            new_item = ""
            while last_item != new_item:
                related_number.append(items[0]['event_id'])
                last_item = items[0]['event_id']
                self.test.appium.swipe_element(items[0], items[0]["width"] + 15, ScreenActions.LEFT, 2500)
                self.test.wait(2)
                elements = self.test.milestones.getElements()
                items = self.test.ui.get_sorted_elements("event_view", "x_pos", elements, "section", related_dic)
                new_item = items[0]['event_id']
            if len(items) > 1:
                for i in range(1, len(items)):
                    related_number.append(items[i]['event_id'])
            swipe_item = len(items) - 1
            self.test.appium.swipe_element(items[swipe_item],
                                           (items[swipe_item]["width"] + 15) * len(related_number),
                                           ScreenActions.RIGHT, 2500)
            self.test.wait(2)
            self.test.log_assert(len(related_number) <= MAX_RELATED_ASSETS, "Too many related assets!")
            # now, verify navigation
            for item in items:
                self.test.wait(2)
                self.test.appium.tap_element(item)
                self.test.wait(2)
                self.verify_active()
                self.test.ui.tap_element("back")

    def scroll_draggable_section(self):
        elements = self.test.milestones.getElements()
        window_width, window_height = self.test.milestones.getWindowSize()
        #"scroll up"
        events_scroller = self.test.milestones.getElement([("id","DraggablePaneView", "==")], elements)
        self.test.appium.swipe_element(events_scroller, window_height / 3, ScreenActions.UP)
        self.test.appium.swipe_element(events_scroller, window_height / 3, ScreenActions.UP)
        elements = self.test.milestones.getElements()
        self.verify_action_menu_revealed(elements)
        #"scroll down"
        events_scroller = self.test.milestones.getElement([("id","DraggablePaneView", "==")], elements)
        self.test.appium.swipe_element(events_scroller, window_height / 3, ScreenActions.DOWN)
        self.test.appium.swipe_element(events_scroller, window_height / 3, ScreenActions.DOWN)
        elements = self.test.milestones.getElements()
        self.verify_action_menu_collapsed(elements)

    def get_seek_bar_elements(self):
        self.navigate()
        milestones = self.test.milestones
        elements = milestones.getElements()
        seek_bar_elements = dict()
        seek_bar_elements['seek_bar_view'] = milestones.getElementContains(elements, "seek_bar_view", "name")
        seek_bar_elements['play_pause_button'] = milestones.getElementContains(elements, "play_pause_button", "name")
        seek_bar_elements['stop_button'] = milestones.getElementContains(elements, "stop_button", "name")
        seek_bar_elements['restart_button'] = milestones.getElementContains(elements, "restart_button", "name")
        seek_bar_elements['trickmode_bar'] = milestones.getElementContains(elements, "trickmode_bar", "name")

        return seek_bar_elements

    def get_linear_event(self, elements):
        linear_event = self.test.milestones.getElement([("event_source", "EVENT_SOURCE_TYPE_LINEAR", "=="), ("event_type", self.event_type, "==")], elements)
        return linear_event

    def get_vod_event(self, elements):
        linear_event = self.test.milestones.getElement([("event_source", "EVENT_SOURCE_TYPE_VOD", "==")], elements)
        return linear_event

    def get_unlock_dic_value(self):
        return self.test.milestones.get_dic_value_by_key("DIC_ACTION_MENU_UNLOCK_BUTTON","general").upper()


class LinearActionMenu(ActionMenu):
    def __init__(self, test):
        ActionMenu.__init__(self, test)

    def verify_record_button(self, is_present):
        self.test.ui.verify_button(self.button_type.RECORD, is_present)

    def verify_cancel_record_button(self, is_present):
        self.test.ui.verify_button(self.button_type.CANCEL, is_present)

    def verify_and_press_button(self, button_type):
        button = self.test.ui.verify_button(button_type, True)
        self.test.appium.tap_element(button)
        self.test.wait(5)

    def verify_and_press_record_button(self):
        self.verify_and_press_button(self.button_type.RECORD)

    def verify_and_press_stop_button(self):
        #self.verify_and_press_button(self.button_type.MANAGE_RECORDINGS)
        self.test.wait(5)
        self.verify_and_press_button(self.button_type.STOP)

    def verify_and_press_delete_button(self):
        self.verify_and_press_button(self.button_type.DELETE)

    def verify_and_press_cancel_booking_button(self):
        self.verify_and_press_button(self.button_type.CANCEL)

    def drag_action_menu_panel(self):
        window_width, window_height = self.test.milestones.getWindowSize()
        stop_y = window_height*1/2
        start_y = window_height*0.8
        pos_x = window_width*1/2
        self.test.mirror.swipe_area(pos_x, start_y, pos_x, stop_y)

    def record_current_event(self, event_title):
        # Record the current event and verify booking
        logging.info("Going to book event:%s from action_menu", event_title)
        self.verify_and_press_record_button()
        #self.test.ui.verify_button(self.button_type.MANAGE_RECORDINGS, True, 10)
        # Wait until recording started
        return self.test.he_utils.wait_for_recording_status(event_title)

    def get_linear_times(self, as_string=False):
        """
        get the start and end time of a liner event from the action menu
        optionally can return it as string

        :param as_string: if True will return string, default to False
        :return: (datetime, datetime )or (str, str)
        """

        device_details = self.test.milestones.getDeviceDetails()
        timezone = pytz.timezone(device_details['timezone'])

        elements = self.test.milestones.getElements()
        event = self.get_linear_event(elements)
        start_time, _, end_time = event['time_text'].split()

        if as_string:
            return start_time, end_time
        else:
            hour, minute = start_time.split(".")
            now = datetime.datetime.now(timezone)
            start_time = now.replace(hour=int(hour), minute=int(minute), second=0)

            # TODO: handle the case the event spans across the day
            hour, minute = end_time.split(".")
            end_time = now.replace(hour=int(hour), minute=int(minute), second=0)

            return start_time, end_time

    def wait_for_seconds_from_event_start(self, seconds=90):
        device_details = self.test.milestones.getDeviceDetails()
        timezone = pytz.timezone(device_details['timezone'])

        start_time, end_time = self.get_linear_times()
        now = datetime.datetime.now(timezone)

        self.test.log("wait_for_seconds_from_event_start: start={}, end={}".format(start_time, end_time))
        if (now - start_time).total_seconds() < seconds:
            return False

        while (now - start_time).total_seconds() < seconds:
            self.test.log("now={}, start_time={} ".format(now, start_time))
            time.sleep(5)
            now = datetime.datetime.now(timezone)

        return True

class VodActionMenu(ActionMenu):
    def __init__(self, test):
        ActionMenu.__init__(self, test)

    def verify_button(self, button_type):
        self.verify_active()
        milestones = self.test.milestones
        elements = milestones.getElements()

        if button_type == self.button_type.PLAY and self.test.project != "KD" and self.test.app_mode == "V2":
            button = milestones.getElement([("id", "play", "==")], elements)
        else:
            key_value = milestones.get_dic_value_by_key(button_type.value)
            if "%s" in key_value:
                button = milestones.getElement([("title_text", key_value.replace("%s", "").upper(), "_)")], elements)
            else:
                button = milestones.getElement([("title_text", key_value.upper(), "==")], elements)

        return button

    def rent_asset(self):
        rent_button = self.verify_button(self.button_type.RENT)
        self.test.log_assert(rent_button, "RENT button not found on screen")
        self.test.appium.tap_element(rent_button)
        self.test.wait(2)

    def play_asset(self, verify_streaming=True, verify_fullscreen=True):
        play_button = self.verify_button(self.button_type.PLAY)
        if not play_button:
            play_button = self.verify_button(self.button_type.RESTART)
        self.test.log_assert(play_button, "PLAY or RESTART button not found on screen")
        self.test.appium.tap_center_element(play_button)
        if verify_fullscreen:
            self.test.screens.fullscreen.verify_active()

        if verify_streaming:
            self.test.screens.playback.verify_streaming_playing()
            self.test.log_assert('VOD' == self.test.screens.playback.get_playback_status()["playbackType"], "playbackType is not VOD")

    '''
        Verifies whether PLAY menu item's presence based on present arg
    '''
    def verify_play_menu(self, present=True):
        self.verify_active()
        play_button = self.verify_button(self.button_type.PLAY)
        if present:
            self.test.log_assert(play_button, "Play button not found on screen")
        else:
            self.test.log_assert(play_button == None, "Play button found on screen")

    def resume_asset(self, verify_streaming=True):
        resume_button = self.verify_button(self.button_type.RESUME)
        self.test.log_assert(resume_button, "Resume button not found on screen")
        self.test.appium.tap_element(resume_button)
        self.test.wait(2)

        if verify_streaming:
            self.test.screens.playback.verify_streaming_playing()
            self.test.log_assert('VOD' == self.test.screens.playback.get_playback_status()["playbackType"], "playbackType is not VOD")

    def play_trailer(self, verify_streaming=True):
        trailer_button = self.verify_button(self.button_type.TRAILER)
        self.test.log_assert(trailer_button, "Trailer button not found on screen")
        self.test.appium.tap_element(trailer_button)
        self.test.wait(2)

    def play_restart_asset(self, verify_streaming=True):
        play_button = self.verify_button(self.button_type.PLAY)
        restart_button = self.verify_button(self.button_type.RESTART)
        self.test.log_assert(play_button or restart_button, "Play/Restart button not found on screen")
        if play_button:
            button = play_button
        else:
            button = restart_button

        self.test.appium.tap_center_element(button)
        self.test.wait(2)

        if verify_streaming:
            self.test.screens.playback.verify_streaming_playing()
            self.test.log_assert('VOD' == self.test.screens.playback.get_playback_status()["playbackType"], "playbackType is not VOD")

    def press_stop(self):
        appium = self.test.appium
        seek_bar = self.get_seek_bar_elements()
        currentTuned = self.test.screens.playback.get_current_tuned()
        if seek_bar['stop_button']:
            appium.tap_element(seek_bar['stop_button'])
            self.test.screens.playback.verify_streaming_stopped(currentTuned)
            return True
        else:
            return False

    def press_play_pause(self):
        appium = self.test.appium
        seek_bar = self.get_seek_bar_elements()
        if seek_bar['play_pause_button']:
            appium.tap_element(seek_bar['play_pause_button'])
            return True
        else:
            return False

    def press_restart(self):
        appium = self.test.appium
        seek_bar = self.get_seek_bar_elements()
        if seek_bar['restart_button']:
            appium.tap_element(seek_bar['restart_button'])
            return True
        else:
            return False

    '''
    The function returns the x and y position of the SeekBar
    '''
    def get_seek_bar_pos(self):
        milestones = self.test.milestones
        seek_bar_element = milestones.getElement([("name", "seek_bar_view", "==")])
        self.test.log_assert(seek_bar_element, "Seek Bar not present")
        x_pos = int(seek_bar_element['x_pos'])
        y_pos = int(seek_bar_element['y_pos'])
        return x_pos, y_pos

    '''
        The function performs Tap/Swipe Seek on VOD based on isTap argument
    '''
    def seek(self, is_tap, percent=0):
        self.navigate()
        x_pos, y_pos = self.get_seek_bar_pos()
        if is_tap:
            self.seek_on_tap( x_pos, y_pos, percent)
        else:
            current_position = self.get_current_seek_bar_position()
            self.seek_on_swipe(x_pos, y_pos, current_position, percent)

    def verifyTimingLabels(self):
        buffer_time = 5
        seek_bar_elements = self.get_seek_bar_elements()
        position = float(seek_bar_elements['seek_bar_view']['position'])
        width = float(seek_bar_elements['seek_bar_view']['width'])
        current_position = round(float(position/width), 2)

        elapsed_time_label = seek_bar_elements['trickmode_bar']['playback_time']
        total_time_label = seek_bar_elements['trickmode_bar']['duration']

        self.test.log_assert(total_time_label and elapsed_time_label, \
                             "Timing labels are missing, seek bar elements : %s" %str(seek_bar_elements))

        elapsed_time = self.timing_text_to_int(elapsed_time_label)
        total_time = self.timing_text_to_int(total_time_label)
        if total_time > 30:
            buffer_time += int(math.ceil(total_time / 30)) * 3

        time_range = xrange(elapsed_time - buffer_time, elapsed_time + buffer_time)
        self.test.log_assert(int(total_time * current_position) in time_range, \
            "timing labels incorrect. Total time is %d, and on the elapsed is %d while current_position is %f"\
            %(total_time, elapsed_time, current_position))

    def timing_text_to_int(self, timing_text):
        return int(int(timing_text) / 1000)

    '''
        The function performs a tap operation on the seek bar,
        provided with the x,y co-ordinates of SeekBar and
        percentage of video that needs to be seeked
    '''
    def seek_on_tap(self, x_pos, y_pos, percent = 0, verify=True):
        self.navigate()
        percent = int(percent)
        milestones = self.test.milestones
        seek_bar_element = milestones.getElement([("name", "seek_bar_view", "==")])
        self.test.log_assert(seek_bar_element, "Seek Bar element not present")
        tap_x = self.test.mirror.offset(int(x_pos), int(seek_bar_element['width'] * (float(percent)/float(100))))
        self.test.appium.tap(tap_x, y_pos)
        if verify:
            self.test.wait(8)
            self.verifyTimingLabels()
            self.test.appium.tap(tap_x, y_pos)
            self.test.wait(5)


    '''
        The function performs a swipe operation on the seek bar,
        provided with the x,y co-ordinates of SeekBar and the currentPosition of VOD
    '''
    def seek_on_swipe(self, x_pos, y_pos, current_position, percent = 0):
        self.navigate()
        percent = int(percent)
        milestones = self.test.milestones
        seek_bar_element = milestones.getElement([("name", "seek_bar_view", "==")])
        self.test.log_assert(seek_bar_element, "Seek Bar element not present")
        start_x = self.test.mirror.offset(int(x_pos), current_position)
        start_y = y_pos
        stop_x = self.test.mirror.offset(int(x_pos), int(seek_bar_element['width'] * (float(percent)/float(100))))
        stop_y = y_pos
        self.test.appium.swipe_area(start_x, start_y, stop_x, start_y)
        self.test.wait(8)
        self.verifyTimingLabels()
        self.test.appium.swipe_area(start_x, start_y, stop_x, start_y)
        self.test.wait(5)

    '''
        The function returns the position of seek bar of VOD content that has been played
    '''
    def get_current_seek_bar_position(self):
        self.navigate()
        milestones = self.test.milestones
        seek_bar_element = milestones.getElement([("name", "seek_bar_view", "==")])
        self.test.log_assert(seek_bar_element, "Seek Bar not present")
        position = float(seek_bar_element['position'])
        return position

    def calculate_remaining_time(self):
        self.navigate()
        milestones = self.test.milestones
        elements = milestones.getElements()
        seek_bar_element = milestones.getElement([("name", "seek_bar_view", "==")], elements)
        trick_mode_bar = milestones.getElement([("name", "trickmode_bar", "==")], elements)
        self.test.log_assert(seek_bar_element, "Seek Bar not present")
        self.test.log_assert(trick_mode_bar, "Trickmode Bar not present")
        total_time_arr = trick_mode_bar['end_time'].split(":")
        total_time = int(total_time_arr[0]) * 60 + int(total_time_arr[1])
        elapsed_time = float(float(seek_bar_element['position'])/float(seek_bar_element['width']))
        return total_time - int(total_time * elapsed_time)

    def drag_action_menu_panel(self):
        pass

class PvrActionMenu(ActionMenu):
    def __init__(self, test):
        ActionMenu.__init__(self, test)

    def verify_button(self, button_type):
        milestones = self.test.milestones
        elements = milestones.getElements()

        if button_type == self.button_type.PLAY and self.test.project != "KD" and self.test.app_mode == "V2":
            button = self.test.milestones.getElement([("id", "play", "==")], elements)
        else:
            key_value = milestones.get_dic_value_by_key(button_type.value)
            if "%s" in key_value:
                button = milestones.getElement([("title_text", key_value.replace("%s", "").upper(), "_)")], elements)
            else:
                button = milestones.getElement([("title_text", key_value.upper(), "==")], elements)

        return button

    def verify_and_press_delete_button(self):
        button = self.test.ui.verify_button(self.button_type.DELETE, True)

        if self.test.project == "KD":
            yes_button_key = "DIC_GENERIC_YES"
            no_button_key = "DIC_GENERIC_NO"
        else:
            yes_button_key = "DIC_YES"
            no_button_key = "DIC_NO"

        self.test.appium.tap_element(button)
        self.test.screens.notification.verify_notification_message_by_key(self.button_confirmation_text.DELETE.value, type="general")
        self.test.screens.notification.verify_notification_button_name_by_key(yes_button_key)
        self.test.screens.notification.verify_notification_button_name_by_key(no_button_key)
        self.test.screens.notification.tap_notification_button(yes_button_key)
        self.test.wait(5)


    def play_asset(self, verify_streaming=True):
            play_button = self.verify_button(self.button_type.PLAY)
            if not play_button:
                play_button = self.verify_button(self.button_type.RESTART)
            self.test.log_assert(play_button, 'PLAY or RESTART button not found on screen')
            self.test.appium.tap_element(play_button)
            self.test.wait(2)

            if verify_streaming:
                self.test.screens.playback.verify_streaming_playing()
                #playbackType = self.test.screens.playback.get_playback_status()['playbackType']
                #self.test.log_assert('PVR' == playbackType, 'playbackType is not PVR! ({})'.format(playbackType))
                self.test.screens.fullscreen.verify_active()
