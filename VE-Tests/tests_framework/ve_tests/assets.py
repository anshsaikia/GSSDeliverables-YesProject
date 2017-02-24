from tests_framework.ui_building_blocks.screen import ScreenActions
from tests_framework.he_utils.series_utils import *
from tests_framework.ui_building_blocks.K.library_filter import FilterType
from tests_framework.he_utils.cmdc_querys import CMDC as cmdc
from itertools import ifilter
import sys

# abstract (not instantiated) classes
from tests_framework.ve_tests.tests_conf import DeviceType


class Asset(object):
    def common_labels_set(self):
        get_dic_value_by_key = self.test.milestones.get_dic_value_by_key
        screens = self.test.screens
        self.action_record = get_dic_value_by_key(screens.action_menu.button_type.RECORD.value).upper()
        self.manage_recording = get_dic_value_by_key("DIC_TIMELINE_MANAGE_RECORDINGS").upper()
        self.cancel = get_dic_value_by_key(screens.action_menu.button_type.CANCEL.value).upper()
        self.library = get_dic_value_by_key("DIC_MAIN_HUB_LIBRARY").upper()
        self.more_info = get_dic_value_by_key("DIC_TIMELINE_MORE_INFO").upper()
        self.what2delete =  get_dic_value_by_key("DIC_ACTION_MENU_ACTION_DELETE_RECORDING").upper()
        self.cancel_season_episode_string = get_dic_value_by_key("DIC_ACTION_MENU_ACTION_CANCEL_EPISODE_BOOKING").upper()
        self.cancel_season_string = get_dic_value_by_key("DIC_ACTION_MENU_ACTION_CANCEL_SEASON_BOOKING").upper()

    def single_labels_set(self):
        self.common_labels_set()
        get_dic_value_by_key = self.test.milestones.get_dic_value_by_key
        screens = self.test.screens
        self.what2record = get_dic_value_by_key(screens.action_menu.button_type.RECORD.value).upper()
        self.where2go = get_dic_value_by_key(screens.library.filter_type.RECORDINGS.value).upper()
        self.splash = get_dic_value_by_key("DIC_BOOKING_FUTURE_SUCCEEDED").upper()  # "THE SHOW WILL BE RECORDED."

    def episode_labels_set(self):
        self.common_labels_set()
        get_dic_value_by_key = self.test.milestones.get_dic_value_by_key
        screens = self.test.screens
        self.what2record = get_dic_value_by_key(
            "DIC_ACTION_MENU_ACTION_RECORD_THIS_EPISODE").upper()  # "RECORD THIS EPISODE" #
        self.where2go = get_dic_value_by_key(screens.library.filter_type.RECORDINGS.value).upper()
        self.splash = get_dic_value_by_key(
            "DIC_NOTIFICATION_BOOKING_EPISODE_SUCCEEDED").upper()  # "THIS EPISODE WILL BE RECORDED" #
        self.what2delete = "DELETE RECORDING OF THIS EPISODE"
        self.cancel = "CANCEL BOOKING OF THIS EPISODE"

    def __init__(self, test):
        super(Asset, self).__init__()
        self.what2record = None
        self.where2go = None
        self.splash = None
        self.is_series = False
        self.is_timeline = False
        self.is_fullscreen = False
        self.is_book_full_season = False
        self.channel = None  # will be set for series on booking
        self.test = test
        self.manage_recording = None
        self.cancel = None
        self.what2delete = None
        self.library = None
        self.more_info = None
        self.cancel_season_string = None
        self.cancel_season_episode_string = None

    # currently is used only by grid_check
    def channel_title(self):
        channel, event = self.test.he_utils.get_channel_to_record_current_event(remaining_time_minutes=3)
        self.test.log('get_channel_to_record_current_event returned logical channel {}'.format(channel))
        return str(channel)

    def if_need(self, method):
        """ calling method if it exists in the object (if need you should have)"""
        try:
            m = getattr(self, method)
        except AttributeError:
            return
        m()

    def scroll_to_channel_by_sek(self):
        self.test.screens.fullscreen.tune_to_channel_by_sek(self.channel.serviceEquivalenceKey)

    def check_booking(self, title):
        """whait for library to be not empty and Check that it has 1 element with name title"""
        self.goto_library()
        for i in range(40):
            # compare the recorded asset title with the first one in the library
            elements = self.test.milestones.getElements()
            #  self.test.log( 'all elements =' + elements)
            elements = self.test.milestones.getElementsArray([("event_type", "EVENT_CONTENT_TYPE_STANDALONE", "==")])
            #  self.test.log( 'elements =' + elements)
            if elements:
                self.test.log('elements[0]["title_text"] =' + elements[0]["title_text"] + " title = " + title)
                self.test.log_assert(len(elements) == 1, "len(elements) =" + str(len(elements)))
                self.test.log_assert(elements[0]["title_text"].upper().split(":")[0] in title.upper(),
                                     "booked = " + repr(title) + "!= 1st recorded:" + elements[0]["title_text"])
                return
            else:
                elements = self.test.milestones.getElements()
                element = self.test.milestones.getElement([("id", "back", "==")], elements)
                self.test.appium.tap_element(element)
                self.test.wait(1)
                self.test.ui.verify_and_press_button_by_title(self.where2go)
                self.test.wait(1)

        self.test.log_assert(False, "Libray is empty")

    def press_exit(self):
        self.test.ui.wait_for_element("exit")
        self.test.wait(1)   #without this it doesn't find "exit"

        self.test.ui.verify_and_press_button_by_title("exit", "id")

    def goto_library(self):
        self.if_need("go2action_menu4library")
        self.press_exit()
        self.test.screens.header.tap_item("DIC_MAIN_HUB_LIBRARY")
        self.test.milestones.getElements()  # wait
        for i in range(2):
            self.test.ui.one_finger_swipe(ScreenActions.UP)
        self.test.ui.verify_and_press_button_by_title(self.where2go)


class ActionMenu(Asset):
    """ActionMenu Asset"""

    def __init__(self, test):
        super(ActionMenu, self).__init__(test)

    def navigate_to_necessary_screen(self):
        self.test.screens.infolayer.show()
        if self.test.device_type == DeviceType.TABLET:
            self.test.ui.tap_element("actionmenu")
        else :
            elements = self.test.milestones.getElements()
            element = self.test.milestones.getElement([("id", "back", "==")], elements)
            self.test.appium.tap_element(element)

    def go2action_menu(self):
        self.test.screens.linear_action_menu.navigate()


class Full(Asset):
    """ Full screen Asset"""

    def __init__(self, test):
        super(Full, self).__init__(test)
        self.is_fullscreen = True

    def go2action_menu4library(self):
        self.test.screens.linear_action_menu.navigate()


class Series(Asset):
    """Season or episode"""

    def __init__(self, test):
        super(Series, self).__init__(test)
        self.is_series = True
        # currently is used only by grid_check:

    def channel_title(self):
        return str(self.test.assets.get_current_episode_channel().logicalChannelNumber)

    def scroll_to_channel(self):
        self.channel = self.test.assets.get_current_episode_channel()
        self.test.log_assert(self.channel.serviceEquivalenceKey)
        self.scroll_to_channel_by_sek()

    def get_channel(self):
        self.channel = self.get_current_episode_channel()
        channel_id = self.channel.serviceEquivalenceKey
        self.test.log_assert(channel_id)
        return channel_id

    def press_action_record(self):
        self.test.ui.wait_for_label(self.action_record)
        self.if_need("go2action_menu")
        self.test.ui.verify_and_press_button_by_title(self.action_record)

    def navigate_to_necessary_screen(self):
        """navigate to menu with RECORD or "Delete recording" button"""
        self.scroll_to_channel()
        self.press_action_record()


class Timeline(Asset):
    """Asset from the timeline screen"""

    def __init__(self, test):
        super(Timeline, self).__init__(test)
        self.is_timeline = True

    def navigate_to_necessary_screen(self):
        """from full screen navigate to timeline,
         scroll to necessary channel and menu with RECORD or STOP RECORDING button"""
        self.test.screens.timeline.navigate()
        self.if_need("scroll_to_channel")

        # Instead of pressing More info, look for live event and press that event to move to action menu

        get_dic_value_by_key = self.test.milestones.get_dic_value_by_key
        if self.test.platform == "iOS" :
            self.test.ui.tap_label(get_dic_value_by_key("DIC_ZAPLIST_LIVE").upper())
        else :
            self.test.ui.tap_label(get_dic_value_by_key("DIC_TIMELINE_NOW").upper())
        self.test.screens.action_menu.verify_active()

    def scroll_to_channel_by_sek(self):
        self.test.screens.timeline.scroll_to_channel_by_sek(self.channel.serviceEquivalenceKey)

    def press_exit(self):
        for i in range(3):
            super(Timeline, self).press_exit()


# concreete classes
class Channel(object):
    """channel information"""

    def __init__(self, logical_channel_number, service_equivalence_key, season_id, test):
        self.logicalChannelNumber = logical_channel_number
        self.serviceEquivalenceKey = service_equivalence_key
        self.seasonID = season_id
        test.log('channel Number={}, Key={}'.format(logical_channel_number, service_equivalence_key))

        ''' PPS on Amstel seems doesn't work properly. check when it will.
        self.serviceId = service_id
        self.offerId = offer_id
        '''


class SingleEventAsset(ActionMenu):
    def __init__(self, test):
        super(SingleEventAsset, self).__init__(test)

    def labels_set(self):
        self.single_labels_set()

class EpisodeAsset(Series, ActionMenu):
    def __init__(self, test):
        super(EpisodeAsset, self).__init__(test)

    def labels_set(self):
        self.episode_labels_set()

    def press_manage_recording(self):
        self.test.ui.wait_for_label(self.manage_recording)
        self.test.ui.verify_and_press_button_by_title(self.manage_recording)

class SeasonAsset(Series, ActionMenu):
    def __init__(self, test):
        super(SeasonAsset, self).__init__(test)
        self.is_book_full_season = True

    def labels_set(self):
        self.common_labels_set()
        get_dic_value_by_key = self.test.milestones.get_dic_value_by_key
        screens = self.test.screens
        self.what2record = get_dic_value_by_key(
            "DIC_ACTION_MENU_ACTION_RECORD_THIS_SEASON").upper()  # "RECORD THIS SEASON" #
        self.where2go = get_dic_value_by_key(screens.library_filter.filter_type.SCHEDULED.value).upper()
        self.splash = get_dic_value_by_key(
            "DIC_NOTIFICATION_BOOKING_SEASON_SUCCEEDED").upper()  # "THIS SEASON WILL BE RECORDED." #

    def check_booking(self, title):
        """ Check that booked episods in CMDC and PPS are the same
            TBD: compare with the library list"""
        hh_id = self.test.configuration["he"]["generated_household"]

        self.test.wait(12)  # waiting for booking of the entire series (usually takes ~6 seconds)
        logging.info("Getting data from pps")
        all_bookings = get_all_bookings_from_PPS(self.test, hh_id)
        logging.info("all_bookings: ", all_bookings)
        ep_bookings = get_episodes_from_pps(all_bookings)
        logging.info("ep_bookings: ", ep_bookings)

        series_id = ep_bookings.keys()[0]
        # service_id = get_series_channels_from_pps(all_bookings)[series_id][0]

        logging.info("Getting data from CMDC")
        cmdc_eps, totalEpisodes = cmdc.get_all_season_episodes(self.test, season_id=series_id)
        data_episodes_of_series_from_cmdc = episodes_of_series_from_cmdc(cmdc_eps, series_id)

        logging.info("All season episodes from CMDC\n")
        for episode in cmdc_eps:
            logging.info(str(episode) + "\n")

        logging.info("compare data, between cmdc and pps")
        episodes_list_from_pps = ep_bookings[series_id]
        episodes_list_from_cmdc = []
        for episode in data_episodes_of_series_from_cmdc:
            episodes_list_from_cmdc.append(episode['id'])
        compare_episodes_lists(series_id, episodes_list_from_pps, episodes_list_from_cmdc)

    def record_from_action_menu(self, asset):
        self.labels_set()
        title = self.test.assets.generic_book_record_action(asset)
        self.test.screens.library_filter.navigate()
        self.test.screens.library_filter.navigate_to_manage_recording_filter(FilterType.SCHEDULED)
        elements = self.test.milestones.getElements()

        # tap on first booked event (should be latest to be booked)
        for element in elements:
            if (("event_source" in element and element["event_source"] == "EVENT_SOURCE_TYPE_PVR") or  # Android
                    ("event_type" in element and element["event_type"] == "EVENT_TYPE_PVR_ASSET") or ("event_type" in element and element["event_type"] == "EVENT_CONTENT_TYPE_STANDALONE") ):  # iOS
                self.test.appium.tap_element(element)
                break
        self.test.ui.verify_and_press_button_by_title(self.manage_recording)


class FullSingleEventAsset(Full):
    def __init__(self, test):
        super(FullSingleEventAsset, self).__init__(test)

    def labels_set(self):
        self.single_labels_set()


class FullEpisodeAsset(Full, Series):
    def __init__(self, test):
        super(FullEpisodeAsset, self).__init__(test)

    def labels_set(self):
        self.episode_labels_set()


class TimelineEpisode(Timeline, EpisodeAsset):
    def __init__(self, test):
        super(TimelineEpisode, self).__init__(test)

    def press_manage_recording(self):
        self.test.ui.wait_for_label(self.manage_recording)
        self.test.ui.verify_and_press_button_by_title(self.manage_recording)


class TimelineSingleEvent(Timeline, SingleEventAsset):
    def __init__(self, test):
        super(TimelineSingleEvent, self).__init__(test)

    def scroll_to_channel(self):
        self.channel = self.test.assets.get_current_single_event_channel()
        self.test.log_assert(self.channel)
        self.test.log_assert(self.channel.serviceEquivalenceKey)
        self.scroll_to_channel_by_sek()


class VeTestAssets:
    def __init__(self, test):
        self.test = test
        self.single_event = SingleEventAsset(test)
        self.episode = EpisodeAsset(test)
        self.season = SeasonAsset(test)
        self.full_single_event = FullSingleEventAsset(test)
        self.full_episode = FullEpisodeAsset(test)
        self.timeline_episode = TimelineEpisode(test)
        self.timeline_single_event = TimelineSingleEvent(test)

    def generic_book_record_action(self, asset):
        """Navigate to necessary screen and tap RECORD or STOP RECORDING button"""
        #  navigate to full screen
        event = self.find_event(False)
        orig_screen = self.test.milestones.get_current_screen()
        self.test.appium.tap_element(event)
        self.test.screens.wait_for_screen(orig_screen, is_match=False, retries=30)
        self.test.milestones.getElements()  # self.test.wait(3)
        # navigate to necessary screen and record button
        asset.if_need("navigate_to_necessary_screen")
        title = self.record_event_action(asset)

        return title

    def wait_for_recording_status(self, event_title, status='RECORDING', retries=90):
        from vgw_test_utils.headend_util import get_all_catalog
        state_filter = "state=" + status
        for i in range(retries):
            catalog = get_all_catalog(filter_to_use=state_filter)
            for event in catalog:
                if 'content' in event:
                    if event['content']['title'].upper() == event_title.upper():
                        return event
            logging.info("event:%s is still not in state:%s ...", event_title, status)

            self.test.wait(3)
        logging.info(False, "Fail to find event:{} in status:{}".format(event_title, status))

    def record_and_stop_recording(self, asset):
        #  record
        title = self.generic_book_record_action(asset)
        household_id = self.test.configuration["he"]["generated_household"]
        self.test.Settings['household_id'] = household_id
        self.test.Settings["device_id"] = self.test.he_utils.getDeviceIdFromDeviceAndHH(None, household_id)
        self.wait_for_recording_status(title)
        #  stop recording
        asset.what2record = "STOP RECORDING"
        asset.splash = None
        title = self.generic_book_record_action(asset)

        # hit the confiramtion screen
        notification_msg = self.test.milestones.get_dic_value_by_key("DIC_RECORDING_STOP_CONFIRMATION")
        self.test.screens.notification.verify_notification_message(notification_msg)
        self.test.screens.notification.tap_notification_button("DIC_YES")
        self.wait_for_recording_status(title, "RECORDED")

        return title

    def find_event(self, poster=True):
        """
        Find the asset element in the current screen (first poster(poster=True) or (poster=False) first event)
        This function is too fixed to the graphics order therefore easily breakable
        Called from a few screens in order to find the first/only asset on screen.-
        :param poster: if taking the asset from the
        :return: element
        """
        # TODO: find a better way to recognize an asset should be called only from a "known screens"
        # TODO: a title should be collected before taping on it (not from actionmenu)
        not_ready = "This channel cannot be played back on this device."
        found = None
        elements = self.test.milestones.getElements()
        window_width, window_height = self.test.milestones.getWindowSize()
        y_pos = window_height
        title = not_ready
        for element in elements:
            if ('name' in element and
                        'title_text' in element and
                        element['title_text'] is not None and
                    not element['title_text'] == '' and
                    not element['title_text'].startswith('test') and
                    not element['title_text'].startswith('ON AIR') and
                    not element['title_text'].startswith('SEE ALL') and
                    not element['title_text'].startswith('DIRECTORS')):

                if (not poster) or (element['name'] == 'text_view' and element['y_pos'] < y_pos):
                    y_pos = element['y_pos']
                    title = element['title_text']
                    found = element
                    if not poster or ('id' in element and element['id'] == 'info_title'):
                        break
        self.test.log("title =" + title)
        return found

    def record_event_action(self, asset, check_splash=False):
        """ press asset.what2record button and check for splash if check_splash=True"""
        # remember the recorded asset title
        self.test.ui.wait_for_label(asset.what2record)

        self.test.ui.verify_and_press_button_by_title(asset.what2record, wait=False)
        if asset.splash and check_splash and (self.test.platform == "iOS"):
            self.test.ui.wait_for_label(asset.splash)
            self.test.ui.wait_for_label_removed(asset.splash)
        element = self.find_event()
        asset.title = element['title_text']
        self.test.log("title = " + asset.title)

        return asset.title

    def generic_book_record_and_check(self, asset):
        title = self.generic_book_record_action(asset)
        asset.check_booking(title)

    def generic_book(self, asset, check_splash=True):
        title = self.record_event_action(asset, check_splash)
        return title

    def find_element_in_lib(self, title):
        elements = self.test.milestones.getElementsArray([("event_type", "UNKNOWN", "==")])
        return filter(lambda element: element["title_text"].upper() == title.upper(), elements)

    def check_title_not_in_lib(self, title):
        elements = self.find_element_in_lib(title)
        if elements:
            self.test.appium.tap_element(elements[0])
            self.test.milestones.verifyElement("NO TITLE AVAILABLE")

    def cancel_season_action_menu(self, asset):
        self.test.ui.wait_for_label(asset.cancel_season_string)
        self.test.ui.verify_and_press_button_by_title(asset.cancel_season_string, wait=False)

        self.test.ui.verify_and_press_button_by_title("exit", "id")
        self.test.screens.library_filter.navigate()
        self.check_title_not_in_lib(asset.title)


    def check_cancel(self, asset):
        """ Book Recording, cancel recording and check that event not in the library"""
        title = self.generic_book_record_action(asset)
        if self.test.ui.label_exists_with_wait(asset.manage_recording) :
            self.test.ui.tap_element(asset.manage_recording)

        if asset.is_series:
            cancel_string = asset.cancel_season_episode_string
        else:
            cancel_string = asset.cancel

        self.test.ui.wait_for_label(cancel_string)
        self.test.ui.verify_and_press_button_by_title(cancel_string, wait=False)
        asset.goto_library()
        self.check_title_not_in_lib(title)

    def grid_check(self, asset):
        """ book recording from grid and check the booking"""

        self.test.screens.guide.navigate()
        #self.test.ui.wait_for_label('1')
        self.test.wait(3)

        title = asset.channel_title()

        # TODO: use guide.tune_to_channel_by_sek, when it will be fixed
        cx, cy, elements = self.grid_chanel_coordinates(title)
        asset1 = self.asset_nearest2chanel(cx, cy, elements)
        self.test.appium.tap_element(asset1)
        # wait for HE response
        self.test.milestones.getElements()  # wait
        asset.if_need("press_manage_recording")
        title = self.record_event_action(asset)
        asset.check_booking(title)

    def asset_nearest2chanel(self, cx, cy, elements):
        """ :return the asset nearest to chanel (on screen)"""
        window_width, window_height = self.test.milestones.getWindowSize()
        dx0 = window_width
        dy0 = window_height
        self.test.log("dx0 = {} dy0 = {}".format(dx0, dy0))
        for element in elements:
            if 'name' in element and 'title_text' in element and element['name'] == 'text_view':
                dx = element['x_pos'] - cx
                dy = element['y_pos'] - cy
                self.test.log(u"dx0 = {} dy0 = {} : {}".format(dx0, dy0, element['title_text']))
                if 0 < dx <= dx0 and 0 <= dy <= dy0:
                    asset1 = element
                    dx0 = dx
                    dy0 = dy
                    self.test.log("dx0 = {} dy0 = {} asset1 = {}".format(dx0, dy0, asset1))
            else:
                self.test.log("element = {}".format(element))
        self.test.log_assert(asset1, "no assets on screen")
        return asset1

    def grid_get_all_elements(self, tries=10, delay_seconds=1):
        for x in xrange(tries):
            elements = self.test.milestones.getElements()
            number_of_populated_assets = len([dict for dict in elements if 'event_id' in dict.keys()])
            if number_of_populated_assets > 0:
                break
            else:
                self.test.log('waiting for grid to be populated... (try number {} out of {})'.format(x, tries))
                self.test.wait(delay_seconds)
        self.test.log_assert(number_of_populated_assets > 0, 'grid is not populated after {} seconds!'.format(tries))
        return elements

    def grid_chanel_coordinates(self, title):
        """ :return coordinates of chanel named title"""
        chanel = None
        element1 = None
        while not chanel:
            elements = self.grid_get_all_elements()
            for element in elements:
                if 'name' in element and 'title_text' in element and element['name'] == 'text_view':
                    # no necessary title in the list, if we got the first element the second time
                    if element['title_text'] == '1':
                        if element1:
                            self.test.log_assert(element1 != element, "element1 =" + element1 +
                                                 " element=" + element)
                        else:
                            element1 = element
                    if element['title_text'] == title:
                        chanel = element
                        cx = chanel['x_pos']
                        cy = chanel['y_pos']
                        return cx, cy, elements
            self.test.ui.one_finger_swipe(ScreenActions.UP)
            self.test.milestones.getElements()  # wait
        self.test.log_assert(chanel)

    def get_current_episode_channel(self):
        """ finds a channel on which current episode end time is at least 1 minutes away"""
        return self.get_current_event_channel(True)

    def get_current_single_event_channel(self):
        """ finds a channel on which current single event end time is at least 1 minutes away"""
        return self.get_current_event_channel(False)

    def get_current_event_channel(self, is_series):
        """ finds a channel on which current event end time is at least 1 minutes away"""
        ve_test = self.test
        abr_channels = ve_test.he_utils.abr_services
        current_time = int(time.time()) * 1000
        start_time = current_time
        end_time = start_time + 86400000  # jump 1 day
        events = (ve_test.he_utils.get_current_service_event(start_time, end_time, ch, 1) for ch in abr_channels)
        events = ifilter(None, events)  # only True
        channel = Channel(sys.maxint, None, None, self.test)
        for event in events:
            group = False
            services_ = event["services"][0]
            contents_ = services_["contents"][0]
            even_start_time = contents_["broadcastDateTime"]
            even_duration = contents_["duration"]
            event_end_time = even_start_time + even_duration
            # if evenEndTime time is more than 1 minutes away
            if ("logicalChannelNumber" in services_) and (services_["logicalChannelNumber"] < channel.logicalChannelNumber):
                self.test.log("Channel {}({}) times: start:{}, current:{}, end:{}, group:{}, series:{}".
                              format(services_["logicalChannelNumber"], contents_['serviceEquivalenceKey'],
                                     even_start_time/1000, current_time/1000, event_end_time/1000, group, is_series))
                if (event_end_time > 0) and \
                        (even_start_time < current_time) and \
                        ((event_end_time - current_time) > 60000):
                    if "parentGroups" in contents_:
                        series_groups = (group for group in contents_["parentGroups"] if group['groupType'] == "Series")
                        group = next(series_groups, False)
                    if group:
                        if is_series:
                            channel = Channel(services_["logicalChannelNumber"], contents_['serviceEquivalenceKey'],
                                              group['groupId'].split('//')[1], self.test)
                            # to check when Amstel will be fixed:
                            # group['groupId'].split('//')[1], services_["id"], services_["offerIdList"][0])

                            #break

                    elif not is_series:
                        channel = Channel(services_["logicalChannelNumber"], contents_['serviceEquivalenceKey'],
                                          None, self.test)
                        #break
        if channel.logicalChannelNumber < sys.maxint:
            return channel
        else:
            return False

    def record_stop_and_delete(self, asset):
        """ stop and delete recording """
        test = self.test
        # from test_delete_recording_library_action_menu
        test.screens.full_content_screen.tap_event_by_title(asset.title)
        test.screens.linear_action_menu.verify_active()
        asset.if_need("press_manage_recording")
        test.screens.linear_action_menu.verify_and_press_stop_button()

        test.screens.notification.verify_notification_message("Are you sure that you want to stop this recording?")
        test.screens.notification.get_and_tap_notification_button("DIC_YES")
        # in iOS should refresh
        test.screens.library_filter.go_to_previous_screen()
        test.screens.full_content_screen.tap_event_by_title(asset.title)
        test.screens.linear_action_menu.verify_active()
        asset.if_need("press_manage_recording")
 
        # verify that action has updated to "DELETE RECORDING"
        test.ui.verify_and_press_button_by_title(asset.what2delete)
        test.screens.notification.verify_notification_message("Are you sure that you want to delete this recording?")
        test.screens.notification.get_and_tap_notification_button("DIC_YES")
        # verify that we are back at library filter scheduled and that it is empty
        test.wait(5)
        test.log_assert(test.milestones.get_current_screen() == "full_content_screen", "Failed returning to Library")
        test.log_assert(test.screens.full_content_screen.screen_empty(), "Library is not empty after recording deleted")
